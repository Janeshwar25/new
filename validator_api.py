from flask import Flask, request, jsonify
import subprocess
import sys
import os
import re
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
SCRIPTS_DIR = r"C:\Users\jchowdha\Desktop\AccelQ_AI_Framework\scripts"
OUTPUT_DIR = Path(SCRIPTS_DIR) / "Output"

ACCELQ_INPUT_FILE = r"C:\Users\jchowdha\ACCELQAgent_1\AgentInstances\agent\user_data\AccelQ_Input_&Optup_File.xlsx"
ACCELQ_SHEET_NAME = "BnE_Member_Maintenance"


def normalize_group_ids(value):
    """
    Convert Excel B2 value into clean Member Group ID list.
    Supports:
    3118035
    3118035,3118036
    3118035;3118036
    New line separated values
    """

    if value is None or pd.isna(value):
        return []

    if isinstance(value, float) and value.is_integer():
        value = str(int(value))
    else:
        value = str(value).strip()

    if not value:
        return []

    parts = re.split(r"[,;\n\r\t]+", value)

    group_ids = []

    for item in parts:
        item = item.strip()

        if not item:
            continue

        if item.endswith(".0") and item[:-2].isdigit():
            item = item[:-2]

        group_ids.append(item)

    return group_ids


def read_group_ids_from_accelq_excel():
    """
    Always read Member Group IDs from ACCELQ workbook:
    Sheet: BnE_Member_Maintenance
    Cell: B2
    """

    df = pd.read_excel(
        ACCELQ_INPUT_FILE,
        sheet_name=ACCELQ_SHEET_NAME,
        header=None
    )

    cell_value = df.iloc[1, 1]   # Row 2, Column 2 = B2

    return normalize_group_ids(cell_value)


def extract_report_file(stdout_text):
    """
    Extract generated report file from validator output.
    """

    if not stdout_text:
        return ""

    for line in stdout_text.splitlines():
        if "Report" in line and "reports/" in line:
            return line.split("reports/", 1)[-1].strip()

    return ""


def normalize_output_path(path_value, default_path):
    if not path_value:
        return str(default_path)

    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = Path(SCRIPTS_DIR) / candidate

    return str(candidate)


def build_id_card_output_paths(pdf_path, request_data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_stem = Path(pdf_path).stem or "id_card"
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", pdf_stem).strip("_") or "id_card"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{safe_stem}_{timestamp}"

    return {
        "output": normalize_output_path(
            request_data.get("output") or request_data.get("report"),
            OUTPUT_DIR / f"{base_name}_Validation_Report.xlsx"
        ),
        "extracted_json": normalize_output_path(
            request_data.get("extractedJson") or request_data.get("extracted_json"),
            OUTPUT_DIR / f"{base_name}_Extracted_ID_Card_Data.json"
        ),
        "result_json": normalize_output_path(
            request_data.get("resultJson") or request_data.get("result_json"),
            OUTPUT_DIR / f"{base_name}_Validation_Result.json"
        ),
    }


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def run_validator(script_name):
    """
    Common runner for Group and Member validators.

    IMPORTANT:
    This intentionally ignores the incoming ACCELQ request payload.
    ACCELQ can pass:
        {"group_ids":["ACCELQ"]}
    but actual MG(s) will always be read from Excel B2.
    """

    try:
        group_ids = read_group_ids_from_accelq_excel()
        source = "accelq_excel_b2"

        if not group_ids:
            return jsonify({
                "returncode": 1,
                "source": source,
                "group_ids": [],
                "error": "No Member Group IDs found in ACCELQ Excel B2.",
                "excel_file": ACCELQ_INPUT_FILE,
                "sheet": ACCELQ_SHEET_NAME,
                "cell": "B2"
            }), 400

        cmd = [sys.executable, script_name] + group_ids

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=SCRIPTS_DIR,
            env=env
        )

        return jsonify({
            "returncode": result.returncode,
            "source": source,
            "group_ids": group_ids,
            "script": script_name,
            "report_file": extract_report_file(result.stdout),
            "stdout": result.stdout,
            "stderr": result.stderr
        })

    except Exception as e:
        return jsonify({
            "returncode": 1,
            "script": script_name,
            "error": str(e),
            "excel_file": ACCELQ_INPUT_FILE,
            "sheet": ACCELQ_SHEET_NAME,
            "cell": "B2"
        }), 500


def run_id_card_validator():
    request_data = request.get_json(silent=True) or {}

    pdf_path = (request_data.get("pdf") or request_data.get("pdfPath") or request_data.get("pdf_path") or "").strip()
    payload_path = (request_data.get("payload") or request_data.get("payloadPath") or request_data.get("payload_path") or "").strip()
    payload_json = request_data.get("payloadJson") or request_data.get("payload_json") or ""

    if not pdf_path:
        return jsonify({
            "returncode": 1,
            "error": "Missing required field: pdf",
            "expected": {
                "pdf": "C:/path/to/id_card.pdf",
                "payload": "C:/path/to/alpha_payload.json",
                "payloadJson": "optional raw JSON string",
                "failOnMismatch": False
            }
        }), 400

    if not payload_path and not payload_json:
        return jsonify({
            "returncode": 1,
            "error": "Provide either payload or payloadJson."
        }), 400

    output_paths = build_id_card_output_paths(pdf_path, request_data)

    cmd = [
        sys.executable,
        "ID_Card_Validator.py",
        "--pdf",
        pdf_path,
        "--output",
        output_paths["output"],
        "--extracted-json",
        output_paths["extracted_json"],
        "--result-json",
        output_paths["result_json"],
    ]

    if payload_path:
        cmd.extend(["--payload", payload_path])
    else:
        cmd.extend(["--payload-json", payload_json])

    if parse_bool(request_data.get("failOnMismatch") or request_data.get("fail_on_mismatch")):
        cmd.append("--fail-on-mismatch")

    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=SCRIPTS_DIR,
            env=env
        )

        result_payload = {}
        result_json_path = Path(output_paths["result_json"])
        if result_json_path.exists():
            with open(result_json_path, "r", encoding="utf-8") as file_obj:
                result_payload = json.load(file_obj)

        return jsonify({
            "returncode": result.returncode,
            "script": "ID_Card_Validator.py",
            "pdf": pdf_path,
            "payload": payload_path,
            "usedPayloadJson": bool(payload_json and not payload_path),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "report": output_paths["output"],
            "extractedJson": output_paths["extracted_json"],
            "resultJson": output_paths["result_json"],
            "result": result_payload
        }), (200 if result.returncode == 0 else 400)

    except Exception as exc:
        return jsonify({
            "returncode": 1,
            "script": "ID_Card_Validator.py",
            "error": str(exc),
            "pdf": pdf_path,
            "payload": payload_path
        }), 500


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "running",
        "message": "Validator API is active",
        "available_endpoints": [
            "/run-group-validator",
            "/run-member-validator",
            "/run-id-card-validator"
        ],
        "excel_file": ACCELQ_INPUT_FILE,
        "sheet": ACCELQ_SHEET_NAME,
        "cell": "B2"
    })


@app.route("/run-group-validator", methods=["POST"])
def run_group_validator():
    return run_validator("group_validator.py")


@app.route("/run-member-validator", methods=["POST"])
def run_member_validator():
    return run_validator("member_validator.py")


@app.route("/run-id-card-validator", methods=["POST"])
def run_id_card_validator_route():
    return run_id_card_validator()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )