import sys
import os
import glob
import re
import time
import random
import mysql.connector
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "reports")
ERRQ_HOST = "172.19.96.26"
ERRQ_DB = "errq01"
SOURCE_DBS = ["aquarius_tent01", "tent01_bootes"]

EXPECTED = [
    "memberID",
    "Subscriber ID Card Serial Number",
    "memGroupID",
    "MG_Name",
    "Member Create Date",
    "Member Create Time",
    "socialSecurityNumber",
    "nameLast",
    "nameFirst",
    "gender",
    "birthDate",
    "state",
    "memberProviderID",
    "providerID",
    "covlevelcode",
    "relationshipcode",
    "effectiveDate",
    "expirationdate",
    "memberDirectBillingInd",
    "MemBenefitEffDate",
    "MemBenefitExpDate",
    "MemBeneDeleteInd",
    "Plan Name",
    "Plan Option",
    "benefitBundleID",
    "benefitbundleoptionid",
    "networkscheduleid",
    "benefitStatusCode"
]

OUTPUT_COLUMNS = ["SourceDB"] + EXPECTED

AUDIT_OUTPUT_COLUMNS = [
    "Benefit Create Date",
    "Benefit Create Time",
    "Benefit Create User ID",
    "Benefit Change Date",
    "Benefit Change Time",
    "Benefit Change User ID"
]

OUTPUT_COLUMNS = ["SourceDB"] + EXPECTED + AUDIT_OUTPUT_COLUMNS

# Fields monitored for change detection between the previous member validation report and current run.
TRACKED_CHANGE_FIELDS = [
    "nameLast",
    "nameFirst",
    "gender",
    "birthDate",
    "state",
    "expirationdate",
    "MemBenefitEffDate",
    "MemBenefitExpDate",
    "MemBeneDeleteInd",
    "Plan Name",
    "Plan Option",
    "benefitBundleID",
    "benefitbundleoptionid",
    "networkscheduleid",
    "benefitStatusCode",
    "memberProviderID",
    "providerID"
]

CHANGE_HISTORY_FILE = os.path.join(REPORTS_FOLDER, "member_change_history.xlsx")

# ACCELQ input workbook update settings.
# The script writes one random Subscriber ID Card Serial Number into F2.

ACCELQ_USER_DATA_FOLDER = r"C:\Users\jchowdha\ACCELQAgent_1\AgentInstances\agent\user_data"
ACCELQ_INPUT_WORKBOOK = os.path.join(ACCELQ_USER_DATA_FOLDER, "AccelQ_Input_&Optup_File.xlsx")
ACCELQ_INPUT_SHEET = "BnE_Member_Maintenance"
ACCELQ_SCID_TARGET_CELL = "F2"
ACCELQ_SCID_SOURCE_COLUMN = "Subscriber ID Card Serial Number"
ACCELQ_NEW_MEMBER_TARGET_CELL = "H2"
ACCELQ_NEW_MEMBER_SOURCE_COLUMN = "Member ID"

REASONS = {
    "Subscriber ID Card Serial Number": "No external ID with type=SC in subsaffiliationexternalid",
    "Member Create Date": "createDateTime not populated in SubsAffiliation",
    "Member Create Time": "createDateTime not populated in SubsAffiliation",
    "Plan Name": "No MemberBenefit record for this member or planID is blank",
    "Plan Option": "No MemberBenefit record for this member or planoptionid is blank",
    "benefitBundleID": "No MemberBenefit record or benefitBundleID is blank",
    "benefitbundleoptionid": "No MemberBenefit record or benefitbundleoptionid is blank",
    "networkscheduleid": "No MemberBenefit record or networkscheduleid is blank",
    "benefitStatusCode": "No MemberBenefit record or benefitStatusCode is blank",
    "MemBenefitEffDate": "No MemberBenefit record or benefit effective date is blank",
    "MemBenefitExpDate": "No MemberBenefit record or benefit expiration date is blank",
    "MemBeneDeleteInd": "No MemberBenefit record or delete indicator is blank",
    "covlevelcode": "No coverage level in memberbenefitcovlevelcode",
    "socialSecurityNumber": "Member not found in memb01.memberssnview",
    "state": "No address record in memb01.memberaddress",
    "memberProviderID": "No provider assigned in memberprovider",
    "providerID": "No provider assigned in memberprovider",
    "nameLast": "Member not found in memb01.member",
    "nameFirst": "Member not found in memb01.member",
    "gender": "Member not found in memb01.member",
    "birthDate": "Member not found in memb01.member",
    "MG_Name": "Group not found in membergroup.memgroup",
    "relationshipcode": "Relationship code not set on SubsAffiliation",
    "effectiveDate": "Effective date not set on SubsAffiliation",
    "expirationdate": "Expiration date not set on SubsAffiliation",
    "memberDirectBillingInd": "Direct billing indicator not set on SubsAffiliation"
}

CONNS = {}


def get_conn(db):
    if db in CONNS and CONNS[db].is_connected():
        return CONNS[db]

    if db == "errq01":
        if hasattr(config, "ALPHA_DBS") and "errq01" in config.ALPHA_DBS:
            d = config.ALPHA_DBS["errq01"]
            host = d.get("host", ERRQ_HOST)
            database = d.get("database", ERRQ_DB)
        else:
            host = ERRQ_HOST
            database = ERRQ_DB
        user = config.DB_USER
        password = config.get_db_password()
        port = config.DB_PORT
    else:
        d = config.ALPHA_DBS[db]
        host = d["host"]
        database = d["database"]
        user = config.DB_USER
        password = config.get_db_password()
        port = config.DB_PORT

    CONNS[db] = mysql.connector.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        connection_timeout=30
    )
    return CONNS[db]


def close_conns():
    for c in CONNS.values():
        try:
            c.close()
        except Exception:
            pass
    CONNS.clear()


def q(db, sql, params=None, label=""):
    try:
        return pd.read_sql(sql, get_conn(db), params=params)
    except Exception as e:
        print(f"  WARNING [{label} - {db}]: {str(e)[:180]}")
        return pd.DataFrame()


def ph(values):
    return ",".join(["%s"] * len(values))


def query_sources(sql, params, label):
    frames = []
    for db in SOURCE_DBS:
        df = q(db, sql, params, label)
        if not df.empty:
            df["SourceDB"] = db
            frames.append(df)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()


def get_group_names(gids):
    if not gids:
        return pd.DataFrame()
    sql = f"SELECT memGroupID, memGroupName AS MG_Name FROM memgroup WHERE memGroupID IN ({ph(gids)})"
    return q("membergroup", sql, tuple(gids), "group names")


def get_base_members(gid):
    sql = """
        SELECT DISTINCT
            subsaffiliationid,
            subscriberID,
            MemberID AS memberID,
            MemGroupID AS memGroupID,
            createDateTime,
            relationshipcode,
            effectiveDate,
            expirationdate,
            memberDirectBillingInd
        FROM SubsAffiliation
        WHERE MemGroupID = %s
    """
    df = query_sources(sql, (gid,), "base members")
    if not df.empty:
        df = df.drop_duplicates(subset=["SourceDB", "subsaffiliationid"], keep="first")
    return df


def get_benefits(subs_keys):
    if subs_keys.empty:
        return pd.DataFrame()
    frames = []
    for src in subs_keys["SourceDB"].dropna().unique().tolist():
        ids = subs_keys.loc[subs_keys["SourceDB"] == src, "subsaffiliationid"].dropna().unique().tolist()
        if not ids:
            continue
        sql = f"""
            SELECT
                subsaffiliationid,
                memberbenefitid,
                planID AS `Plan Name`,
                planoptionid AS `Plan Option`,
                benefitBundleID,
                benefitbundleoptionid,
                networkscheduleid,
                benefitStatusCode,
                benplaneffdate AS MemBenefitEffDate,
                benplanexpdate AS MemBenefitExpDate,
                deleteind AS MemBeneDeleteInd,
                createDateTime AS benefitCreateDateTime,
                createUserID AS benefitCreateUserID,
                changeDateTime AS benefitChangeDateTime,
                changeUserID AS benefitChangeUserID
            FROM MemberBenefit
            WHERE subsaffiliationid IN ({ph(ids)})
        """
        df = q(src, sql, tuple(ids), "benefits")
        if not df.empty:
            df["SourceDB"] = src
            frames.append(df)
    if frames:
        out = pd.concat(frames, ignore_index=True)
        return out.drop_duplicates(subset=["SourceDB", "subsaffiliationid"], keep="first")
    return pd.DataFrame()


def get_covlevel(benefit_keys):
    if benefit_keys.empty or "memberbenefitid" not in benefit_keys.columns:
        return pd.DataFrame()
    frames = []
    for src in benefit_keys["SourceDB"].dropna().unique().tolist():
        ids = benefit_keys.loc[benefit_keys["SourceDB"] == src, "memberbenefitid"].dropna().unique().tolist()
        if not ids:
            continue
        sql = f"SELECT memberbenefitid, covlevelcode FROM memberbenefitcovlevelcode WHERE memberbenefitid IN ({ph(ids)})"
        df = q(src, sql, tuple(ids), "covlevel")
        if not df.empty:
            df["SourceDB"] = src
            frames.append(df)
    if frames:
        out = pd.concat(frames, ignore_index=True)
        return out.drop_duplicates(subset=["SourceDB", "memberbenefitid"], keep="first")
    return pd.DataFrame()


def get_scid(subs_keys):
    if subs_keys.empty:
        return pd.DataFrame()
    frames = []
    for src in subs_keys["SourceDB"].dropna().unique().tolist():
        ids = subs_keys.loc[subs_keys["SourceDB"] == src, "subsaffiliationid"].dropna().unique().tolist()
        if not ids:
            continue
        sql = f"""
            SELECT subsaffiliationid, affiliationExternalID AS `Subscriber ID Card Serial Number`
            FROM subsaffiliationexternalid
            WHERE externalIDType = 'SC'
              AND subsaffiliationid IN ({ph(ids)})
        """
        df = q(src, sql, tuple(ids), "SCID")
        if not df.empty:
            df["SourceDB"] = src
            frames.append(df)
    if frames:
        out = pd.concat(frames, ignore_index=True)
        return out.drop_duplicates(subset=["SourceDB", "subsaffiliationid"], keep="first")
    return pd.DataFrame()


def get_provider(member_ids):
    if not member_ids:
        return pd.DataFrame()
    frames = []
    for src in SOURCE_DBS:
        sql = f"SELECT memberID, memberProviderID, providerID FROM memberprovider WHERE memberID IN ({ph(member_ids)})"
        df = q(src, sql, tuple(member_ids), "provider")
        if not df.empty:
            df["ProviderSourceDB"] = src
            frames.append(df)
    if frames:
        out = pd.concat(frames, ignore_index=True)
        return out.drop_duplicates(subset=["memberID"], keep="first")
    return pd.DataFrame()


def get_member_basic(member_ids):
    if not member_ids:
        return pd.DataFrame()
    sql = f"SELECT memberID, nameLast, nameFirst, gender, birthDate FROM member WHERE memberID IN ({ph(member_ids)})"
    return q("memb01", sql, tuple(member_ids), "member basic")


def get_ssn(member_ids):
    if not member_ids:
        return pd.DataFrame()
    sql = f"SELECT memberID, socialSecurityNumber FROM memberssnview WHERE memberID IN ({ph(member_ids)})"
    df = q("memb01", sql, tuple(member_ids), "SSN")
    return df.drop_duplicates(subset=["memberID"]) if not df.empty else df


def get_state(member_ids):
    if not member_ids:
        return pd.DataFrame()
    sql = f"SELECT memberID, state FROM memberaddress WHERE memberID IN ({ph(member_ids)})"
    df = q("memb01", sql, tuple(member_ids), "state")
    return df.drop_duplicates(subset=["memberID"]) if not df.empty else df


def get_member_errors(gids):
    if not gids:
        return pd.DataFrame()
    sql = f"""
        SELECT a.memberID, a.memGroupID,
               b.queueItemDetailErrorCode,
               b.queueItemDetailErrorDescription
        FROM memberenrollmenterrorqueue a
        JOIN memberenrollmenterrorqueueanddetailview b
          ON a.memberEnrollmentErrorQueueID = b.memberEnrollmentErrorQueueID
        WHERE a.memGroupID IN ({ph(gids)})
          AND b.queueItemDetailErrorCode LIKE 'ERR%'
    """
    return q("errq01", sql, tuple(gids), "member error queue")


def get_group_errors(gids):
    if not gids:
        return pd.DataFrame()
    sql = f"""
        SELECT *
        FROM memgrouperrorqueuebulkcloseview
        WHERE memGroupID IN ({ph(gids)})
          AND queueItemDetailErrorCode LIKE 'ERR%'
    """
    return q("errq01", sql, tuple(gids), "group error queue")



def normalize_for_compare(value):
    """
    Normalize values before comparing old vs new values.
    This removes false positives caused by Excel/Pandas formatting:
    0.0 == 0, 1070655360.0 == 1070655360, 1080876983.0 == 1080876983.
    """
    if pd.isna(value) or value is None:
        return ""

    try:
        if isinstance(value, (pd.Timestamp, datetime)):
            if pd.isna(value):
                return ""
            return value.strftime("%m/%d/%Y")
    except Exception:
        pass

    value_str = str(value).strip()
    if value_str.lower() in ["nan", "none", "nat"]:
        return ""

    try:
        if re.fullmatch(r"-?\d+\.0+", value_str):
            return str(int(float(value_str)))
        if re.fullmatch(r"-?\d+", value_str):
            return value_str
        numeric_value = float(value_str)
        if numeric_value.is_integer() and re.fullmatch(r"-?\d+(\.0+)?", value_str):
            return str(int(numeric_value))
    except Exception:
        pass

    try:
        parsed = pd.to_datetime(value_str, errors="coerce")
        if pd.notna(parsed) and any(token in value_str for token in ["/", "-", ":"]):
            return parsed.strftime("%m/%d/%Y")
    except Exception:
        pass

    return value_str


def build_member_key(df):
    """Build stable key for comparison: SourceDB + memGroupID + memberID."""
    df = df.copy()
    for col in ["SourceDB", "memGroupID", "memberID"]:
        if col not in df.columns:
            df[col] = ""
    df["CompareKey"] = (
        df["SourceDB"].astype(str).str.strip()
        + "|"
        + df["memGroupID"].astype(str).str.strip()
        + "|"
        + df["memberID"].astype(str).str.strip()
    )
    return df


def find_previous_member_report(current_report_path):
    """
    Find the latest previous member validation report from the reports folder.
    This avoids using latest_member_snapshot.xlsx files and directly compares report-to-report.
    """
    pattern = os.path.join(REPORTS_FOLDER, "member_validation_*.xlsx")
    candidates = []
    current_abs = os.path.abspath(current_report_path)

    for file_path in glob.glob(pattern):
        file_name = os.path.basename(file_path)
        if file_name.startswith("~$"):
            continue
        if os.path.abspath(file_path) == current_abs:
            continue
        if file_name.lower() in ["member_change_history.xlsx", "latest_member_snapshot.xlsx"]:
            continue
        candidates.append(file_path)

    if not candidates:
        return None

    candidates.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return candidates[0]


def format_audit_timestamp(value):
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return ""
    return parsed.strftime("%m/%d/%Y %I:%M:%S %p")


def detect_removed_members(current_df, report_filename, current_report_path, run_timestamp):
    removed_rows = []
    history_rows = []

    previous_report = find_previous_member_report(current_report_path)
    if not previous_report:
        msg = pd.DataFrame({"Message": ["No previous member validation report found. Removed Members will populate from the next run."]})
        return msg, pd.DataFrame(), None

    try:
        previous_df = pd.read_excel(previous_report, sheet_name="All Members Data")
    except Exception as e:
        msg = pd.DataFrame({"Message": [f"Unable to read previous report for comparison: {previous_report}. Error: {e}"]})
        return msg, pd.DataFrame(), None

    current_df = build_member_key(current_df)
    previous_df = build_member_key(previous_df)

    previous_keys = set(previous_df["CompareKey"].dropna().tolist())
    current_keys = set(current_df["CompareKey"].dropna().tolist())
    removed_keys = previous_keys - current_keys

    previous_indexed = previous_df.set_index("CompareKey")
    previous_report_name = os.path.basename(previous_report)

    for key in removed_keys:
        row = previous_indexed.loc[key]
        record = {
            "Change Detected Timestamp": run_timestamp,
            "Previous Report": previous_report_name,
            "Current Report": report_filename,
            "SourceDB": row.get("SourceDB", ""),
            "Group ID": row.get("memGroupID", ""),
            "Member ID": row.get("memberID", ""),
            "Member Name": f"{row.get('nameLast', '')}, {row.get('nameFirst', '')}".strip(", "),
            "Changed Field": "Member Record",
            "Old Value": "Member existed in previous report",
            "New Value": "",
            "Change Type": "REMOVED MEMBER"
        }
        removed_rows.append(record)
        history_rows.append(record)

    removed_df = pd.DataFrame(removed_rows) if removed_rows else pd.DataFrame({"Message": ["No removed members detected compared with previous report"]})
    return removed_df, pd.DataFrame(history_rows), previous_report_name


def detect_member_changes(current_df, report_filename, current_report_path):
    """
    Compare current member data against the most recent previous member_validation_*.xlsx report.
    Output goes directly into Changed Members sheet with Old Value and New Value.
    No latest_member_snapshot.xlsx files are needed.
    """
    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    change_rows = []
    new_rows = []
    history_rows = []

    if current_df.empty:
        msg = pd.DataFrame({"Message": ["No current member data available"]})
        return msg, msg.copy(), msg.copy(), pd.DataFrame()

    run_date = datetime.now().date()
    current_df = current_df.copy()
    current_df["_benefitCreateParsed"] = pd.to_datetime(
        current_df.get("Benefit Create Date", "").fillna("").astype(str).str.strip()
        + " "
        + current_df.get("Benefit Create Time", "").fillna("").astype(str).str.strip(),
        errors="coerce"
    )
    current_df["_benefitChangeParsed"] = pd.to_datetime(
        current_df.get("Benefit Change Date", "").fillna("").astype(str).str.strip()
        + " "
        + current_df.get("Benefit Change Time", "").fillna("").astype(str).str.strip(),
        errors="coerce"
    )

    for _, row in current_df.iterrows():
        create_ts = row.get("_benefitCreateParsed")
        change_ts = row.get("_benefitChangeParsed")
        create_user = normalize_for_compare(row.get("Benefit Create User ID"))
        change_user = normalize_for_compare(row.get("Benefit Change User ID"))
        create_today = pd.notna(create_ts) and create_ts.date() == run_date
        changed_today = pd.notna(change_ts) and change_ts.date() == run_date and (
            pd.isna(create_ts) or change_ts > create_ts or change_user != create_user
        )

        if changed_today:
            record = {
                "Change Detected Timestamp": run_timestamp,
                "Previous Report": "Same-day audit",
                "Current Report": report_filename,
                "SourceDB": row.get("SourceDB", ""),
                "Group ID": row.get("memGroupID", ""),
                "Member ID": row.get("memberID", ""),
                "Member Name": f"{row.get('nameLast', '')}, {row.get('nameFirst', '')}".strip(", "),
                "Changed Field": "Member Benefit History",
                "Old Value": f"Created {format_audit_timestamp(create_ts)} by {create_user}".strip(),
                "New Value": f"Changed {format_audit_timestamp(change_ts)} by {change_user}".strip(),
                "Create User ID": create_user,
                "Create Date Time": format_audit_timestamp(create_ts),
                "Change User ID": change_user,
                "Change Date Time": format_audit_timestamp(change_ts),
                "Change Type": "UPDATED TODAY"
            }
            change_rows.append(record)
            history_rows.append(record)

        if create_today:
            change_type = "NEW MEMBER TODAY" if not changed_today else "NEW MEMBER CREATED TODAY"
            detail = f"Created {format_audit_timestamp(create_ts)} by {create_user}".strip()
            if pd.notna(change_ts) and not pd.isna(create_ts) and change_ts > create_ts:
                detail = f"{detail}; latest change {format_audit_timestamp(change_ts)} by {change_user}".strip("; ")

            record = {
                "Change Detected Timestamp": run_timestamp,
                "Previous Report": "Same-day audit",
                "Current Report": report_filename,
                "SourceDB": row.get("SourceDB", ""),
                "Group ID": row.get("memGroupID", ""),
                "Member ID": row.get("memberID", ""),
                "Member Name": f"{row.get('nameLast', '')}, {row.get('nameFirst', '')}".strip(", "),
                "Changed Field": "Member Record",
                "Old Value": "",
                "New Value": detail,
                "Create User ID": create_user,
                "Create Date Time": format_audit_timestamp(create_ts),
                "Change User ID": change_user,
                "Change Date Time": format_audit_timestamp(change_ts),
                "Change Type": change_type
            }
            new_rows.append(record)
            history_rows.append(record)

    removed_df, removed_history_df, _ = detect_removed_members(current_df, report_filename, current_report_path, run_timestamp)
    if not removed_history_df.empty:
        history_rows.extend(removed_history_df.to_dict("records"))

    changed_df = pd.DataFrame(change_rows) if change_rows else pd.DataFrame({"Message": ["No members show same-day benefit change activity for this run date"]})
    new_df = pd.DataFrame(new_rows) if new_rows else pd.DataFrame({"Message": ["No members were created on this run date"]})
    history_df = pd.DataFrame(history_rows)

    return changed_df, new_df, removed_df, history_df


def append_member_change_history(history_df):
    """Append detected changes to persistent member_change_history.xlsx."""
    if history_df.empty:
        if os.path.exists(CHANGE_HISTORY_FILE):
            try:
                return pd.read_excel(CHANGE_HISTORY_FILE, sheet_name="Member Change History")
            except Exception:
                pass
        return pd.DataFrame({"Message": ["No changes to append to member change history"]})

    if os.path.exists(CHANGE_HISTORY_FILE):
        try:
            existing_history = pd.read_excel(CHANGE_HISTORY_FILE, sheet_name="Member Change History")
            final_history = pd.concat([existing_history, history_df], ignore_index=True)
        except Exception:
            final_history = history_df.copy()
    else:
        final_history = history_df.copy()

    dedupe_columns = [
        col for col in [
            "SourceDB",
            "Group ID",
            "Member ID",
            "Changed Field",
            "Old Value",
            "New Value",
            "Create User ID",
            "Create Date Time",
            "Change User ID",
            "Change Date Time",
            "Change Type"
        ] if col in final_history.columns
    ]
    if dedupe_columns:
        final_history = final_history.drop_duplicates(subset=dedupe_columns, keep="last")

    final_history.to_excel(CHANGE_HISTORY_FILE, sheet_name="Member Change History", index=False)
    return final_history

def analyze(row):
    missing = []
    issue_rows = []
    for field in EXPECTED:
        val = row.get(field)
        if pd.isna(val) or val is None or str(val).strip() == "":
            missing.append(field)
            issue_rows.append({"Missing Field": field, "Reason": REASONS.get(field, "Field not populated")})
    count = len(EXPECTED) - len(missing)
    status = "GOOD" if count == len(EXPECTED) else ("INCOMPLETE" if count >= len(EXPECTED) - 4 else "ISSUES")
    return status, count, missing, issue_rows


def process_group(gid, group_names, summary, quality, issues):
    start = time.time()
    base = get_base_members(gid)
    if base.empty:
        elapsed = round(time.time() - start, 1)
        print(f"  [SKIP] Group {gid}: 0 members in Aquarius/Bootes SubsAffiliation ({elapsed} sec)")
        summary.append({"Group ID": gid, "Group Name": "", "Total Members": 0, "Source DBs": "", "GOOD": 0, "INCOMPLETE": 0, "ISSUES": 0, "Member Error Count": 0, "Group Error Count": 0, "Time (sec)": elapsed, "Status": "NO DATA"})
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    print(f"  Found {base['memberID'].nunique()} base members across: {', '.join(sorted(base['SourceDB'].unique()))}")

    # Create separate date and time columns from SubsAffiliation.createDateTime
    base["_createDateTimeParsed"] = pd.to_datetime(base.get("createDateTime"), errors="coerce")
    base["Member Create Date"] = base["_createDateTimeParsed"].dt.strftime("%m/%d/%Y")
    base["Member Create Time"] = base["_createDateTimeParsed"].dt.strftime("%H:%M:%S")

    member_ids = base["memberID"].dropna().unique().tolist()
    benefits = get_benefits(base[["SourceDB", "subsaffiliationid"]])
    cov = get_covlevel(benefits[["SourceDB", "memberbenefitid"]]) if not benefits.empty and "memberbenefitid" in benefits.columns else pd.DataFrame()
    scid = get_scid(base[["SourceDB", "subsaffiliationid"]])
    basic = get_member_basic(member_ids)
    ssn = get_ssn(member_ids)
    state = get_state(member_ids)
    provider = get_provider(member_ids)

    df = base.copy()
    if not scid.empty:
        df = df.merge(scid, on=["SourceDB", "subsaffiliationid"], how="left")
    if not benefits.empty:
        df = df.merge(benefits, on=["SourceDB", "subsaffiliationid"], how="left")
    if not cov.empty and "memberbenefitid" in df.columns:
        df = df.merge(cov, on=["SourceDB", "memberbenefitid"], how="left")
    for add in [basic, ssn, state, provider]:
        if not add.empty:
            df = df.merge(add, on="memberID", how="left")
    if not group_names.empty:
        df = df.merge(group_names, on="memGroupID", how="left")

    for col in OUTPUT_COLUMNS:
        if col not in df.columns:
            df[col] = None
    for col in ["birthDate", "effectiveDate", "expirationdate", "MemBenefitEffDate", "MemBenefitExpDate"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%m/%d/%Y")
    df["_benefitCreateDateTimeParsed"] = pd.to_datetime(df.get("benefitCreateDateTime"), errors="coerce")
    df["Benefit Create Date"] = df["_benefitCreateDateTimeParsed"].dt.strftime("%m/%d/%Y")
    df["Benefit Create Time"] = df["_benefitCreateDateTimeParsed"].dt.strftime("%H:%M:%S")
    df["Benefit Create User ID"] = df.get("benefitCreateUserID")
    df["_benefitChangeDateTimeParsed"] = pd.to_datetime(df.get("benefitChangeDateTime"), errors="coerce")
    df["Benefit Change Date"] = df["_benefitChangeDateTimeParsed"].dt.strftime("%m/%d/%Y")
    df["Benefit Change Time"] = df["_benefitChangeDateTimeParsed"].dt.strftime("%H:%M:%S")
    df["Benefit Change User ID"] = df.get("benefitChangeUserID")
    df = df[OUTPUT_COLUMNS]

    good = incomplete = bad = 0
    for _, row in df.iterrows():
        member_name = f"{row.get('nameLast','')}, {row.get('nameFirst','')}".strip(", ") or f"Member {row.get('memberID','Unknown')}"
        status, count, missing, issue_list = analyze(row)
        quality.append({
            "SourceDB": row.get("SourceDB"),
            "Group ID": row.get("memGroupID"),
            "Member ID": row.get("memberID"),
            "Member Name": member_name,
            "Member Create Date": row.get("Member Create Date"),
            "Member Create Time": row.get("Member Create Time"),
            "Quality Status": status,
            "Fields Populated": f"{count}/{len(EXPECTED)}",
            "Missing Fields": ", ".join(missing) if missing else "None"
        })
        for issue in issue_list:
            issues.append({
                "SourceDB": row.get("SourceDB"),
                "Group ID": row.get("memGroupID"),
                "Member ID": row.get("memberID"),
                "Member Name": member_name,
                "Missing Field": issue["Missing Field"],
                "Reason": issue["Reason"]
            })
        if status == "GOOD":
            good += 1
        elif status == "INCOMPLETE":
            incomplete += 1
        else:
            bad += 1

    elapsed = round(time.time() - start, 1)
    gname = ""
    if not group_names.empty:
        match = group_names[group_names["memGroupID"].astype(str) == str(gid)]
        if not match.empty:
            gname = str(match.iloc[0]["MG_Name"])
    summary.append({
        "Group ID": gid,
        "Group Name": gname,
        "Total Members": df["memberID"].nunique(),
        "Source DBs": ", ".join(sorted(df["SourceDB"].dropna().unique())),
        "GOOD": good,
        "INCOMPLETE": incomplete,
        "ISSUES": bad,
        "Member Error Count": 0,
        "Group Error Count": 0,
        "Time (sec)": elapsed,
        "Status": "DONE"
    })
    print(f"  [DONE] Group {gid}: {df['memberID'].nunique()} members ({good} GOOD, {incomplete} INCOMPLETE, {bad} ISSUES) in {elapsed} sec")
    return df



def close_excel_workbook_if_open(file_path):
    """
    If the ACCELQ input workbook is open in Excel, save and close that workbook.
    This uses Excel COM automation on Windows. If unavailable, returns SKIPPED.
    """
    try:
        import win32com.client
    except Exception as e:
        return {
            "status": "SKIPPED",
            "message": f"Excel COM not available; workbook may need to be closed manually if locked. Details: {e}"
        }

    try:
        target_path = os.path.abspath(file_path).lower()
        target_name = os.path.basename(file_path).lower()
        excel = win32com.client.GetActiveObject("Excel.Application")

        for wb in list(excel.Workbooks):
            try:
                wb_fullname = str(wb.FullName).lower()
                wb_name = str(wb.Name).lower()

                if wb_fullname == target_path or wb_name == target_name:
                    wb.Save()
                    wb.Close(SaveChanges=True)
                    return {
                        "status": "CLOSED",
                        "message": f"Workbook was open. Saved and closed: {file_path}"
                    }
            except Exception:
                continue

        return {
            "status": "NOT_OPEN",
            "message": "Workbook was not open in Excel."
        }

    except Exception as e:
        return {
            "status": "SKIPPED",
            "message": f"Could not inspect Excel workbooks. Details: {e}"
        }


def update_accelq_input_with_random_scid(current_df):
    """
    Pick one random Subscriber ID Card Serial Number from current member data
    and update ACCELQ input workbook BnE_Member_Maintenance!F2.

    If the workbook is open in Excel, the script attempts to save and close it first,
    then updates F2 and saves the workbook.
    """
    try:
        if current_df is None or current_df.empty:
            return {
                "status": "SKIPPED",
                "message": "No current member data available to pick Subscriber ID Card Serial Number.",
                "selected_scid": ""
            }

        if ACCELQ_SCID_SOURCE_COLUMN not in current_df.columns:
            return {
                "status": "SKIPPED",
                "message": f"Column not found: {ACCELQ_SCID_SOURCE_COLUMN}",
                "selected_scid": ""
            }

        values = []
        for val in current_df[ACCELQ_SCID_SOURCE_COLUMN].dropna().tolist():
            selected = str(val).strip()
            if not selected or selected.lower() in ["nan", "none", "nat"]:
                continue
            if selected.endswith(".0") and selected[:-2].isdigit():
                selected = selected[:-2]
            values.append(selected)

        values = sorted(set(values))

        if not values:
            return {
                "status": "SKIPPED",
                "message": "No valid Subscriber ID Card Serial Number found in current data.",
                "selected_scid": ""
            }

        selected_scid = random.choice(values)

        if not os.path.exists(ACCELQ_INPUT_WORKBOOK):
            return {
                "status": "FAILED",
                "message": f"ACCELQ input workbook not found: {ACCELQ_INPUT_WORKBOOK}",
                "selected_scid": selected_scid
            }

        excel_close_status = close_excel_workbook_if_open(ACCELQ_INPUT_WORKBOOK)

        last_error = ""
        for attempt in range(1, 6):
            try:
                wb = load_workbook(ACCELQ_INPUT_WORKBOOK)

                if ACCELQ_INPUT_SHEET not in wb.sheetnames:
                    wb.close()
                    return {
                        "status": "FAILED",
                        "message": f"Worksheet not found: {ACCELQ_INPUT_SHEET}",
                        "selected_scid": selected_scid,
                        "excel_close_status": excel_close_status
                    }

                ws = wb[ACCELQ_INPUT_SHEET]
                old_value = ws[ACCELQ_SCID_TARGET_CELL].value
                ws[ACCELQ_SCID_TARGET_CELL] = selected_scid
                ws[ACCELQ_SCID_TARGET_CELL].number_format = "@"
                wb.save(ACCELQ_INPUT_WORKBOOK)
                wb.close()

                return {
                    "status": "UPDATED",
                    "message": f"Updated {ACCELQ_INPUT_SHEET}!{ACCELQ_SCID_TARGET_CELL} with Subscriber ID Card Serial Number.",
                    "old_value": old_value,
                    "selected_scid": selected_scid,
                    "target_workbook": ACCELQ_INPUT_WORKBOOK,
                    "target_sheet": ACCELQ_INPUT_SHEET,
                    "target_cell": ACCELQ_SCID_TARGET_CELL,
                    "excel_close_status": excel_close_status,
                    "attempts": attempt
                }

            except PermissionError as e:
                last_error = str(e)
                time.sleep(2)
            except Exception as e:
                last_error = str(e)
                time.sleep(2)

        return {
            "status": "FAILED",
            "message": f"Unable to update workbook after retries. Last error: {last_error}",
            "selected_scid": selected_scid,
            "excel_close_status": excel_close_status
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "message": str(e),
            "selected_scid": ""
        }


def update_accelq_input_with_new_member_id(new_members_df):
    """
    Pick one newly added member ID from the New Members sheet data and update
    ACCELQ input workbook BnE_Member_Maintenance!H2.

    This is separate from F2. F2 is used for Subscriber ID Card Serial Number.
    H2 is used for the newly added Member ID.
    """
    try:
        if new_members_df is None or new_members_df.empty:
            return {
                "status": "SKIPPED",
                "message": "No New Members data available to update H2.",
                "selected_member_id": ""
            }

        if "Message" in new_members_df.columns:
            return {
                "status": "SKIPPED",
                "message": str(new_members_df.iloc[0].get("Message", "No newly added member found.")),
                "selected_member_id": ""
            }

        if ACCELQ_NEW_MEMBER_SOURCE_COLUMN not in new_members_df.columns:
            return {
                "status": "SKIPPED",
                "message": f"Column not found in New Members data: {ACCELQ_NEW_MEMBER_SOURCE_COLUMN}",
                "selected_member_id": ""
            }

        values = []
        for val in new_members_df[ACCELQ_NEW_MEMBER_SOURCE_COLUMN].dropna().tolist():
            selected = str(val).strip()
            if not selected or selected.lower() in ["nan", "none", "nat"]:
                continue
            if selected.endswith(".0") and selected[:-2].isdigit():
                selected = selected[:-2]
            values.append(selected)

        values = sorted(set(values))

        if not values:
            return {
                "status": "SKIPPED",
                "message": "No valid newly added Member ID found.",
                "selected_member_id": ""
            }

        selected_member_id = random.choice(values)

        if not os.path.exists(ACCELQ_INPUT_WORKBOOK):
            return {
                "status": "FAILED",
                "message": f"ACCELQ input workbook not found: {ACCELQ_INPUT_WORKBOOK}",
                "selected_member_id": selected_member_id
            }

        excel_close_status = close_excel_workbook_if_open(ACCELQ_INPUT_WORKBOOK)

        last_error = ""
        for attempt in range(1, 6):
            try:
                wb = load_workbook(ACCELQ_INPUT_WORKBOOK)

                if ACCELQ_INPUT_SHEET not in wb.sheetnames:
                    wb.close()
                    return {
                        "status": "FAILED",
                        "message": f"Worksheet not found: {ACCELQ_INPUT_SHEET}",
                        "selected_member_id": selected_member_id,
                        "excel_close_status": excel_close_status
                    }

                ws = wb[ACCELQ_INPUT_SHEET]
                old_value = ws[ACCELQ_NEW_MEMBER_TARGET_CELL].value
                ws[ACCELQ_NEW_MEMBER_TARGET_CELL] = selected_member_id
                ws[ACCELQ_NEW_MEMBER_TARGET_CELL].number_format = "@"
                wb.save(ACCELQ_INPUT_WORKBOOK)
                wb.close()

                return {
                    "status": "UPDATED",
                    "message": f"Updated {ACCELQ_INPUT_SHEET}!{ACCELQ_NEW_MEMBER_TARGET_CELL} with newly added Member ID.",
                    "old_value": old_value,
                    "selected_member_id": selected_member_id,
                    "target_workbook": ACCELQ_INPUT_WORKBOOK,
                    "target_sheet": ACCELQ_INPUT_SHEET,
                    "target_cell": ACCELQ_NEW_MEMBER_TARGET_CELL,
                    "excel_close_status": excel_close_status,
                    "attempts": attempt
                }

            except PermissionError as e:
                last_error = str(e)
                time.sleep(2)
            except Exception as e:
                last_error = str(e)
                time.sleep(2)

        return {
            "status": "FAILED",
            "message": f"Unable to update H2 after retries. Last error: {last_error}",
            "selected_member_id": selected_member_id,
            "excel_close_status": excel_close_status
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "message": str(e),
            "selected_member_id": ""
        }

def load_groups_from_file(path):
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        return []
    try:
        df = pd.read_excel(path) if path.lower().endswith(".xlsx") else pd.read_csv(path)
        return [str(x) for x in df[df.columns[0]].dropna().tolist()]
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return []


def main(gids):
    start = time.time()
    print("=" * 70)
    print(f"MEMBER VALIDATOR - AQUARIUS + BOOTES | {len(gids)} group(s)")
    print("Strategy: search both source DBs, include all members, explain missing fields, and show changes in Changed Members.")
    print("=" * 70)

    group_names = get_group_names(gids)
    member_errors = get_member_errors(gids)
    group_errors = get_group_errors(gids)

    all_data, summary, quality, issues = [], [], [], []
    for idx, gid in enumerate(gids, 1):
        print(f"\n[{idx}/{len(gids)}] Processing Group: {gid}")
        df = process_group(gid, group_names, summary, quality, issues)
        if not df.empty:
            all_data.append(df)

    member_counts = member_errors.groupby("memGroupID").size().to_dict() if not member_errors.empty and "memGroupID" in member_errors.columns else {}
    group_counts = group_errors.groupby("memGroupID").size().to_dict() if not group_errors.empty and "memGroupID" in group_errors.columns else {}
    for row in summary:
        gid_int = int(row["Group ID"]) if str(row["Group ID"]).isdigit() else row["Group ID"]
        row["Member Error Count"] = int(member_counts.get(gid_int, member_counts.get(str(row["Group ID"]), 0)))
        row["Group Error Count"] = int(group_counts.get(gid_int, group_counts.get(str(row["Group ID"]), 0)))
        if row["Member Error Count"] or row["Group Error Count"]:
            row["Status"] = "ERRORS FOUND"

    close_conns()
    combined = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame(columns=OUTPUT_COLUMNS)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

    accelq_update_status = update_accelq_input_with_random_scid(combined)
    print(f"  ACCELQ Input Update Status : {accelq_update_status.get('status')}")
    print(f"  ACCELQ Selected SCID       : {accelq_update_status.get('selected_scid')}")
    print(f"  ACCELQ Update Message      : {accelq_update_status.get('message')}")
    ts = datetime.now().strftime("%m.%d.%Y.%I.%M%p").lower()
    filename = f"member_validation_{'_'.join(map(str,gids))}_{ts}.xlsx" if len(gids) <= 3 else f"member_validation_bulk_{ts}.xlsx"
    path = os.path.join(REPORTS_FOLDER, filename)

    changed_df, new_members_df, removed_members_df, history_df = detect_member_changes(combined, filename, path)
    member_change_history_df = append_member_change_history(history_df)
    accelq_new_member_update_status = update_accelq_input_with_new_member_id(new_members_df)
    print(f"  ACCELQ H2 New Member Status : {accelq_new_member_update_status.get('status')}")
    print(f"  ACCELQ H2 Member ID         : {accelq_new_member_update_status.get('selected_member_id')}")
    print(f"  ACCELQ H2 Update Message    : {accelq_new_member_update_status.get('message')}")

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        combined.to_excel(writer, sheet_name="All Members Data", index=False)
        pd.DataFrame(quality).to_excel(writer, sheet_name="Member Quality Status", index=False)
        pd.DataFrame(issues).to_excel(writer, sheet_name="Field-Level Issues", index=False)
        changed_df.to_excel(writer, sheet_name="Changed Members", index=False)
        new_members_df.to_excel(writer, sheet_name="New Members", index=False)
        removed_members_df.to_excel(writer, sheet_name="Removed Members", index=False)
        member_change_history_df.to_excel(writer, sheet_name="Member Change History", index=False)
        pd.DataFrame([accelq_update_status]).to_excel(writer, sheet_name="ACCELQ Input Update", index=False)
        pd.DataFrame([accelq_new_member_update_status]).to_excel(writer, sheet_name="ACCELQ New Member Update", index=False)
        (member_errors if not member_errors.empty else pd.DataFrame({"Message": ["No member error queue records found"]})).to_excel(writer, sheet_name="Member Error Queue", index=False)
        (group_errors if not group_errors.empty else pd.DataFrame({"Message": ["No group error queue records found"]})).to_excel(writer, sheet_name="Group Error Queue", index=False)
        pd.DataFrame(summary).to_excel(writer, sheet_name="Summary by Group", index=False)

    total_members = combined["memberID"].nunique() if not combined.empty else 0
    print("\n" + "=" * 70)
    print("MEMBER VALIDATION SUMMARY")
    print("=" * 70)
    print(f"  Total Groups  : {len(gids)}")
    print(f"  Total Members : {total_members}")
    print(f"  Member Errors : {len(member_errors)}")
    print(f"  Group Errors  : {len(group_errors)}")
    print(f"  Total Time    : {round(time.time() - start, 1)} sec")
    print(f"  Report        : reports/{filename}")
    print(f"  ACCELQ F2 SCID: {accelq_update_status.get('selected_scid')}")
    print("=" * 70)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        group_ids = ["3118036"]
        print("No group IDs supplied. Using default 3118036")
    elif args[0] == "--file" and len(args) >= 2:
        group_ids = load_groups_from_file(args[1])
        if not group_ids:
            sys.exit(1)
    else:
        group_ids = [x for x in args if not x.startswith("--")]
    main(group_ids)
