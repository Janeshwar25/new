import sys
import os
import time
import mysql.connector
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "reports")
ERRQ_HOST = "172.19.96.26"
ERRQ_DB = "errq01"
SOURCE_DBS = ["aquarius_tent01", "tent01_bootes"]
CONNS = {}
GROUP_SNAPSHOT_FILE = os.path.join(REPORTS_FOLDER, "latest_group_snapshot.xlsx")
GROUP_TRACKED_FIELDS = ["Group Name", "Source DBs", "Total Checks", "PASS", "FAIL", "WARNING", "Health %", "Status", "Member Error Count", "Group Error Count"]

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
    CONNS[db] = mysql.connector.connect(host=host, port=port, database=database, user=user, password=password, connection_timeout=30)
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

def add(results, gid, category, check, status, details, source_db=""):
    results.append({"Group ID": gid, "SourceDB": source_db, "Category": category, "Check": check, "Status": status, "Details": details})

def query_source_dbs(sql, params, label):
    frames = []
    for db in SOURCE_DBS:
        df = q(db, sql, params, label)
        if not df.empty:
            df["SourceDB"] = db
            frames.append(df)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()

def get_group_info(gid):
    return q("membergroup", "SELECT memGroupID, memGroupName FROM memgroup WHERE memGroupID=%s", (gid,), "memgroup")

def get_contract_info(gid):
    return q("membergroup", "SELECT memGroupContractID, effectiveDate, expirationDate FROM memgroupcontract WHERE memGroupID=%s", (gid,), "contract")

def get_bill_group(gid):
    return q("membergroup", "SELECT billGroupID FROM billgroup WHERE memGroupID=%s", (gid,), "bill group")

def get_membership_data(gid):
    sql = """
        SELECT DISTINCT S.subsaffiliationid, S.subscriberID, S.MemberID, S.MemGroupID,
               S.relationshipcode, S.effectiveDate, S.expirationdate, MB.memberbenefitid,
               MB.planID, MB.planoptionid, MB.benefitBundleID, MB.benefitbundleoptionid,
               MB.networkscheduleid, MB.benefitStatusCode
        FROM SubsAffiliation S
        LEFT JOIN MemberBenefit MB ON S.subsaffiliationid = MB.subsaffiliationid
        WHERE S.MemGroupID = %s
    """
    df = query_source_dbs(sql, (gid,), "membership/plans")
    if not df.empty:
        df = df.drop_duplicates(subset=["SourceDB", "subsaffiliationid", "MemberID"], keep="first")
    return df

def get_member_errors(gids):
    if not gids:
        return pd.DataFrame()
    sql = f"""
        SELECT a.memberID, a.memGroupID, b.queueItemDetailErrorCode,
               b.queueItemDetailErrorDescription
        FROM memberenrollmenterrorqueue a
        JOIN memberenrollmenterrorqueueanddetailview b
          ON a.memberEnrollmentErrorQueueID = b.memberEnrollmentErrorQueueID
        WHERE a.memGroupID IN ({ph(gids)}) AND b.queueItemDetailErrorCode LIKE 'ERR%'
    """
    return q("errq01", sql, tuple(gids), "member error queue")

def get_group_errors(gids):
    if not gids:
        return pd.DataFrame()
    sql = f"""
        SELECT * FROM memgrouperrorqueuebulkcloseview
        WHERE memGroupID IN ({ph(gids)}) AND queueItemDetailErrorCode LIKE 'ERR%'
    """
    return q("errq01", sql, tuple(gids), "group error queue")

def validate_group(gid, all_results, plans_summary, members_summary):
    start = time.time()
    local = []
    group_name = ""
    mg = get_group_info(gid)
    if mg.empty:
        add(local, gid, "Group Core", "Group Exists", "FAIL", "Group not found in membergroup.memgroup")
    else:
        group_name = str(mg.iloc[0].get("memGroupName", ""))
        add(local, gid, "Group Core", "Group Exists", "PASS", "Found")
        add(local, gid, "Group Core", "Group Name", "PASS" if group_name else "WARNING", group_name or "Blank")
    con = get_contract_info(gid)
    if con.empty:
        add(local, gid, "Contract", "Contract Exists", "FAIL", "No contract found")
    else:
        add(local, gid, "Contract", "Contract Exists", "PASS", f"{len(con)} contract row(s)")
        today = datetime.now().date()
        eff_ok = sum(pd.notna(d) and d.date() <= today for d in pd.to_datetime(con["effectiveDate"], errors="coerce"))
        exp_ok = sum(pd.notna(d) and d.date() > today for d in pd.to_datetime(con["expirationDate"], errors="coerce"))
        add(local, gid, "Contract", "Effective Date Valid", "PASS" if eff_ok else "WARNING", f"{eff_ok} valid")
        add(local, gid, "Contract", "Expiration Date Valid", "PASS" if exp_ok else "WARNING", f"{exp_ok} valid")
    mem = get_membership_data(gid)
    total_members = total_subs = active_members = 0
    source_dbs = ""
    if mem.empty:
        add(local, gid, "Membership", "Members Exist", "FAIL", "No records in SubsAffiliation across aquarius_tent01/tent01_bootes")
        add(local, gid, "Plans", "Plan/Benefit Data", "FAIL", "No MemberBenefit data found across aquarius_tent01/tent01_bootes")
    else:
        source_dbs = ", ".join(sorted(mem["SourceDB"].dropna().unique().tolist()))
        total_members = mem["MemberID"].nunique()
        total_subs = mem["subscriberID"].nunique() if "subscriberID" in mem.columns else 0
        active_members = mem[mem["benefitStatusCode"] == "A"]["MemberID"].nunique() if "benefitStatusCode" in mem.columns else 0
        add(local, gid, "Membership", "Members Exist", "PASS", f"{total_members} member(s)", source_dbs)
        add(local, gid, "Membership", "Subscribers Exist", "PASS" if total_subs else "WARNING", f"{total_subs} subscriber(s)", source_dbs)
        add(local, gid, "Membership", "Active Members", "PASS" if active_members else "WARNING", f"{active_members} active member(s)", source_dbs)
        plan_rows = mem[mem["planID"].notna() | mem["planoptionid"].notna() | mem["benefitBundleID"].notna()]
        if plan_rows.empty:
            add(local, gid, "Plans", "Plan/Benefit Data", "FAIL", "Members found, but no MemberBenefit data found", source_dbs)
        else:
            add(local, gid, "Plans", "Plan/Benefit Data", "PASS", f"{len(plan_rows)} row(s)", source_dbs)
            add(local, gid, "Plans", "Plan Name Present", "PASS" if plan_rows["planID"].notna().any() else "WARNING", f"{plan_rows['planID'].notna().sum()} non-null", source_dbs)
            add(local, gid, "Plans", "Plan Option Present", "PASS" if plan_rows["planoptionid"].notna().any() else "WARNING", f"{plan_rows['planoptionid'].notna().sum()} non-null", source_dbs)
            add(local, gid, "Plans", "Active Benefits", "PASS" if (plan_rows["benefitStatusCode"] == "A").any() else "WARNING", f"{(plan_rows['benefitStatusCode'] == 'A').sum()} active", source_dbs)
            for _, r in plan_rows.iterrows():
                plans_summary.append({"Group ID": gid, "SourceDB": r.get("SourceDB"), "Plan Name": r.get("planID"), "Plan Option": r.get("planoptionid"), "Bundle ID": r.get("benefitBundleID"), "Bundle Option": r.get("benefitbundleoptionid"), "Network": r.get("networkscheduleid"), "Benefit Status": r.get("benefitStatusCode")})
    members_summary.append({"Group ID": gid, "Group Name": group_name, "Source DBs": source_dbs, "Total Members": total_members, "Subscribers": total_subs, "Active Members": active_members})
    bg = get_bill_group(gid)
    add(local, gid, "Bill Group", "Bill Group Exists", "PASS" if not bg.empty else "WARNING", f"{len(bg)} bill group row(s)")
    all_results.extend(local)
    actionable = [x for x in local if x["Status"] in ["PASS", "FAIL", "WARNING"]]
    passed = sum(1 for x in actionable if x["Status"] == "PASS")
    failed = sum(1 for x in actionable if x["Status"] == "FAIL")
    warning = sum(1 for x in actionable if x["Status"] == "WARNING")
    total = len(actionable)
    health = round((passed / total) * 100, 1) if total else 0
    status = "HEALTHY" if failed == 0 and warning == 0 else ("ATTENTION" if failed else "INCOMPLETE")
    elapsed = round(time.time() - start, 1)
    print(f"  [{status}] Group {gid}: {passed}/{total} passed, {failed} failed, {warning} warnings ({elapsed} sec)")
    return {"Group ID": gid, "Group Name": group_name, "Source DBs": source_dbs, "Total Checks": total, "PASS": passed, "FAIL": failed, "WARNING": warning, "Health %": health, "Status": status, "Time (sec)": elapsed, "Member Error Count": 0, "Group Error Count": 0}

def normalize_for_compare(value):
    if pd.isna(value) or value is None:
        return ""
    value = str(value).strip()
    if value.lower() in ["nan", "none", "nat"]:
        return ""
    return value

def detect_group_changes(current_df):
    if current_df.empty:
        msg = pd.DataFrame({"Message": ["No current group data available"]})
        return msg, msg.copy(), msg.copy()
    current_df = current_df.copy()
    current_df["CompareKey"] = current_df["Group ID"].astype(str).str.strip()
    if not os.path.exists(GROUP_SNAPSHOT_FILE):
        return (pd.DataFrame({"Message": ["No previous group snapshot found. Current run saved as baseline."]}), pd.DataFrame({"Message": ["No previous snapshot found. New group comparison available from next run."]}), pd.DataFrame({"Message": ["No previous snapshot found. Removed group comparison available from next run."]}))
    previous_df = pd.read_excel(GROUP_SNAPSHOT_FILE, sheet_name="Group Health Dashboard")
    previous_df["CompareKey"] = previous_df["Group ID"].astype(str).str.strip()
    old_keys = set(previous_df["CompareKey"].dropna().tolist())
    new_keys = set(current_df["CompareKey"].dropna().tolist())
    common = old_keys.intersection(new_keys)
    added = new_keys - old_keys
    removed = old_keys - new_keys
    old_i = previous_df.set_index("CompareKey")
    new_i = current_df.set_index("CompareKey")
    changes = []
    for key in common:
        old_row = old_i.loc[key]
        new_row = new_i.loc[key]
        for field in GROUP_TRACKED_FIELDS:
            if field not in old_i.columns or field not in new_i.columns:
                continue
            old_value = normalize_for_compare(old_row.get(field))
            new_value = normalize_for_compare(new_row.get(field))
            if old_value != new_value:
                changes.append({"Group ID": new_row.get("Group ID", ""), "Changed Field": field, "Old Value": old_value, "New Value": new_value, "Change Type": "UPDATED"})
    new_rows = [{"Group ID": new_i.loc[k].get("Group ID", ""), "Change Type": "NEW GROUP"} for k in added]
    rem_rows = [{"Group ID": old_i.loc[k].get("Group ID", ""), "Change Type": "REMOVED GROUP"} for k in removed]
    return (pd.DataFrame(changes) if changes else pd.DataFrame({"Message": ["No group status changes detected"]}), pd.DataFrame(new_rows) if new_rows else pd.DataFrame({"Message": ["No new groups detected"]}), pd.DataFrame(rem_rows) if rem_rows else pd.DataFrame({"Message": ["No removed groups detected"]}))

def prepare_plans_summary(plans_summary):
    if not plans_summary:
        return pd.DataFrame({"Message": ["No plan rows found"]})
    plans_df = pd.DataFrame(plans_summary)
    dedup_cols = ["Group ID", "SourceDB", "Plan Name", "Plan Option", "Bundle ID", "Bundle Option", "Network", "Benefit Status"]
    existing_cols = [c for c in dedup_cols if c in plans_df.columns]
    if existing_cols:
        plans_df = plans_df.drop_duplicates(subset=existing_cols, keep="first")
    sort_cols = [c for c in ["Group ID", "Plan Name", "Plan Option"] if c in plans_df.columns]
    if sort_cols:
        plans_df = plans_df.sort_values(sort_cols)
    return plans_df

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
    print(f"GROUP VALIDATOR - AQUARIUS + BOOTES | {len(gids)} group(s)")
    print("=" * 70)
    member_errors = get_member_errors(gids)
    group_errors = get_group_errors(gids)
    dashboard, all_results, plans_summary, members_summary = [], [], [], []
    for idx, gid in enumerate(gids, 1):
        print(f"\n[{idx}/{len(gids)}] Validating Group: {gid}")
        dashboard.append(validate_group(gid, all_results, plans_summary, members_summary))
    member_counts = member_errors.groupby("memGroupID").size().to_dict() if not member_errors.empty and "memGroupID" in member_errors.columns else {}
    group_counts = group_errors.groupby("memGroupID").size().to_dict() if not group_errors.empty and "memGroupID" in group_errors.columns else {}
    for row in dashboard:
        gid_int = int(row["Group ID"]) if str(row["Group ID"]).isdigit() else row["Group ID"]
        row["Member Error Count"] = int(member_counts.get(gid_int, member_counts.get(str(row["Group ID"]), 0)))
        row["Group Error Count"] = int(group_counts.get(gid_int, group_counts.get(str(row["Group ID"]), 0)))
        if row["Member Error Count"] or row["Group Error Count"]:
            row["Status"] = "ERRORS FOUND"
    issues = [x for x in all_results if x["Status"] in ["FAIL", "WARNING"]]
    close_conns()
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    ts = datetime.now().strftime("%m.%d.%Y.%I.%M%p").lower()
    filename = f"group_validation_{'_'.join(map(str,gids))}_{ts}.xlsx" if len(gids) <= 3 else f"group_validation_bulk_{ts}.xlsx"
    path = os.path.join(REPORTS_FOLDER, filename)
    dashboard_df = pd.DataFrame(dashboard)
    group_changes_df, new_groups_df, removed_groups_df = detect_group_changes(dashboard_df)
    plans_df_final = prepare_plans_summary(plans_summary)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        dashboard_df.to_excel(writer, sheet_name="Group Health Dashboard", index=False)
        pd.DataFrame(all_results).to_excel(writer, sheet_name="Detailed Results", index=False)
        (pd.DataFrame(issues) if issues else pd.DataFrame({"Message": ["No validation issues found"]})).to_excel(writer, sheet_name="Issues Summary", index=False)
        group_changes_df.to_excel(writer, sheet_name="Group Status Changes", index=False)
        new_groups_df.to_excel(writer, sheet_name="New Groups", index=False)
        removed_groups_df.to_excel(writer, sheet_name="Removed Groups", index=False)
        (member_errors if not member_errors.empty else pd.DataFrame({"Message": ["No member error queue records found"]})).to_excel(writer, sheet_name="Member Error Queue", index=False)
        (group_errors if not group_errors.empty else pd.DataFrame({"Message": ["No group error queue records found"]})).to_excel(writer, sheet_name="Group Error Queue", index=False)
        plans_df_final.to_excel(writer, sheet_name="Plans Summary", index=False)
        pd.DataFrame(members_summary).to_excel(writer, sheet_name="Members Summary", index=False)
    dashboard_df.to_excel(GROUP_SNAPSHOT_FILE, sheet_name="Group Health Dashboard", index=False)
    print("\n" + "=" * 70)
    print("GROUP VALIDATION SUMMARY")
    print("=" * 70)
    print(f"  Total Groups  : {len(gids)}")
    print(f"  Member Errors : {len(member_errors)}")
    print(f"  Group Errors  : {len(group_errors)}")
    print(f"  Total Time    : {round(time.time() - start, 1)} sec")
    print(f"  Report        : reports/{filename}")
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
