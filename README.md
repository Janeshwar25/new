# Technical Guide — forge-projectplan-generation

## Overview

This repository is a **full-stack AI-assisted project plan management platform**. It integrates with Aha (roadmapping), Rally, Smartsheet (output), Optics (financials), and MongoDB (persistence) to automate the generation, updating, and analysis of project plans and financial reports.

The system has two primary surfaces:
- A **Streamlit UI** for users to interact with a chat agent and trigger plan generation.
- A **FastAPI backend** that handles plan building logic, Smartsheet updates, and agent orchestration.

---

## Setup

### Secure Groups Required

To access Github repo, make sure you request these secure groups:
- `polaris_dev`
- `Azu_Technology_Employer_And_Individual`

### GitHub Set Up and Repo Clone

After secure-group access is approved, set up GitHub access and clone the repository.

1. Verify your GitHub account has access to the organization/repository.
2. Configure Git identity on your machine:
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "your_email@uhg.com"
  ```
3. Choose an authentication method:
  - SSH (recommended):
    ```bash
    ssh-keygen -t ed25519 -C "your_email@uhg.com"
    cat ~/.ssh/id_ed25519.pub
    ```
    Add the public key to your GitHub account, then test:
    ```bash
    ssh -T git@github.com
    ```
  - HTTPS (PAT): use a GitHub Personal Access Token when prompted for password.
4. Clone the repository:
  ```bash
  cd ~/Documents
  git clone https://github.com/uhc-tech-employer-individual/forge-projectplan-generation/
  cd forge-projectplan-generation
  ```
5. Pull latest updates:
  ```bash
  git pull origin main
  ```

### Icarus API Set Up

Use the official references below for onboarding and endpoint details:
- https://docs.hcp.uhg.com/ot-datahub/icarus-overview
- https://insights.hcp.uhg.com/api/icarus/v1/docs#/

The Icarus API credentials are your **MSID username and password**. In this codebase, those are loaded from environment variables:
- `ICARUS_USERNAME`
- `ICARUS_PASSWORD`

Recommended setup flow:
1. Confirm secure-group access is approved.
2. Populate `ICARUS_USERNAME` and `ICARUS_PASSWORD` in your local env file.
3. Validate by calling the token endpoint (`/login/access-token`) and checking that an `access_token` is returned.

The code I have built should provide the structure you need to just replace the env variables with your MSID credentials.

---

## Data Access

All external data is fetched via direct HTTP calls using the `requests` library. SSL verification is disabled system-wide (`verify=False`) due to the UHG corporate proxy. Auth headers and base URLs are centralized in `config.py`.

---

### Aha

Aha is the product roadmap tool. Data is fetched using a **Bearer token** passed as an HTTP header.

The primary function is `get_aha_data(idea)` in `engine/mapping.py`. Given an Aha idea ID (e.g. `GNP-I-1234`), it pulls the idea record, walks its `custom_fields` to extract the Optics PRJ number, initiative tag, and Oversight Approved Amount, then follows linked `master_feature` and `custom_object_links` records to build the list of impacted apps.

**Sample call:**
```python
headers = config.get_aha_headers()  # {"Authorization": "Bearer <AHA_API_KEY>"}
url = f"{config.AHA_BASE_URL}/ideas/GNP-I-1234"
idea = requests.get(url, headers=headers, verify=False, timeout=30).json()["idea"]
```

Aha is also queried for initiative names:
```python
url = f"{config.AHA_BASE_URL}/initiatives/{initiative_id}"
initiative = requests.get(url, headers=headers, verify=False, timeout=30).json()["initiative"]["name"]
```

---

### Icarus API (Rally + Financials)

Icarus is UHG's internal data API which in this case is serving two types of data:
- **Delivery data** — Rally hierarchy (strategic themes → capabilities → features)
- **Finance data** — Optics PRJ-level costs (actuals, ETCs, EACs)

Both use the same **two-step auth flow**: POST credentials to get a short-lived JWT, then pass it as a Bearer token on subsequent GET requests. Responses are returned as CSV and parsed directly into pandas DataFrames.

**Step 1 — Obtain access token:**
```python
token_url = f"{config.ICARUS_BASE_URL}/login/access-token"
response = requests.post(token_url, data={"username": config.ICARUS_USERNAME, "password": config.ICARUS_PASSWORD}, verify=False)
access_token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
```

**Step 2a — Fetch Rally delivery data (strategic themes → capabilities → features):**
```python
# Get all strategic themes, find the ID for a given theme number (e.g. ST15926)
theme_url = f"{config.ICARUS_BASE_URL}/domains/delivery/collections/agile_strategic_theme/csv?columns=strategic_theme_id&columns=strategic_theme_nbr"
themes = pd.read_csv(StringIO(requests.get(theme_url, headers=headers, verify=False).content.decode("utf-8")))
theme_id = themes[themes["strategic_theme_nbr"] == "ST15926"]["strategic_theme_id"].values[0]

# Get solution capabilities under that theme
capability_url = f"https://insights.hcp.uhg.com/api/icarus/v1/domains/delivery/collections/agile_solution_capability/csv?columns=solution_capability_id&columns=parent_id&columns=title&columns=solution_capability_state"
capabilities = pd.read_csv(StringIO(requests.get(capability_url, headers=headers, verify=False).content.decode("utf-8")))
```

Note: Rally data is **not fetched directly from Rally**. It is accessed through the Icarus Data Catalog Explorer, which mirrors Rally's hierarchy. The underlying data originates from `rally1.rallydev.com` but is queried exclusively via the Icarus endpoints.

**Step 2b — Fetch Optics financials for a PRJ:**
```python
# Returns monthly labor cost slices for a given Optics project ID
dce_url = f"{config.ICARUS_BASE_URL}/domains/finance/collections/ppmo_work_effort_resource/csv?slicetype=MONTHLY&project_id=PRJ12345"
df = pd.read_csv(StringIO(requests.get(dce_url, headers=headers, verify=False).content.decode("utf-8")))

# Labor cost is derived from hours × blended rate (Onshore: $145/hr, Offshore: $46/hr)
df["estimated_cost"] = np.where(df["onshore_offshore"] == "Onshore", df["actual_l_hours"] * 145, df["actual_l_hours"] * 46)
df["etc_l_cost"]     = np.where(df["onshore_offshore"] == "Onshore", df["etc_l_hours"]    * 145, df["etc_l_hours"]    * 46)
```

---

## Folder Structure

### `app/`
The web application layer.

| File | Purpose |
|------|---------|
| `app.py` | Streamlit frontend. Renders the chat UI, handles user input, calls the FastAPI backend at `/chat`, and renders responses (including formatted tables, email draft buttons, and report downloads). |
| `routes.py` | FastAPI backend. Exposes `/chat` and `/financials` endpoints. Routes requests to the plan builder (`engine/mapping.py`), project agent (`agent/project_agent.py`), or Smartsheet updater (`upload/update_smartsheet.py`). |

**How they connect:** `app.py` sends HTTP POST requests to `routes.py`. `routes.py` is the orchestration hub that calls all downstream modules.

---

### `engine/`
Core data processing and plan-building logic. The heart of the system.

| File | Purpose |
|------|---------|
| `mapping.py` | Primary plan builder. Contains `build_plan()`, which pulls data from Aha, Rally, and Optics, merges it against an Excel template, and produces a structured pandas DataFrame representing a full project plan. Also contains `get_aha_data()`, `get_optics()`, `get_optics_financials()`, and `get_aha_os()` for pulling from individual external systems. |
| `mongodb_helper.py` | MongoDB client wrapper. Provides `MongoDBHelper` class used across the codebase to read/write plan metadata, notes, and financial records to MongoDB. |
| `utils.py` | Shared utilities: reading Excel templates, saving plan metadata to JSON or MongoDB, and other helper functions used by both the engine and the app layer. |
| `test_dashboard.py` | Generates PET (Pre-Enter-Test) test scripts from plan DataFrames. Called from the Streamlit UI to produce downloadable test artifacts. |
| `__init__.py` | Marks `engine/` as a Python package. |

---

### `upload/`
Handles all outbound writes to Smartsheet.

| File | Purpose |
|------|---------|
| `smartsheet_export.py` | Creates brand-new Smartsheet sheets from a DataFrame. Used for project plan uploads. Handles column definitions, row hierarchy (indentation levels), formatting, and row-level retry logic (3 attempts per row). Folder routing is tag-driven (CMP, CEP, RLE, Specialty). |
| `update_smartsheet.py` | Updates existing Smartsheet sheets — refreshes cells from Rally/Optics data. Also contains `smartsheet_to_pandas()` for reading a live sheet back into a DataFrame. Used by the `/chat` update flow and the agent sync process. |
| `__init__.py` | Marks `upload/` as a Python package. |

---

### `agent/`
LLM-powered agent layer for natural language interaction.

| File | Purpose |
|------|---------|
| `project_agent.py` | Core LangGraph agent. Implements a `ProjectAgent` class with a stateful agentic loop. The agent can answer questions about active projects, generate email drafts, create alerts, look up financials, and perform cross-project searches. Tools are defined inline using `@tool` decorators. |
| `azure_llm.py` | Factory for the Azure OpenAI `AzureChatOpenAI` LangChain client. Reads credentials from config. |
| `prompts.py` | System prompts for the LLM. Contains `PROJECT_AGENT_SYSTEM_PROMPT` — the instruction set that defines the agent's persona, capabilities, and formatting rules. |
| `llm_context_builder.py` | Pulls project metadata and Smartsheet markdown from MongoDB and formats it into structured context strings for the LLM. Provides functions like `get_project_context()`, `get_all_active_projects_context()`, and `search_projects_by_criteria()`. |
| `needs_attention_analyzer.py` | Analyzes project data to flag items that need attention (schedule slippage, budget variance, etc.) for use in agent alerts. |
| `alert_constants.py` | Defines alert type constants and thresholds used by `needs_attention_analyzer.py`. |
| `sync_smartsheet_markdown.py` | Standalone sync job. Walks the MMI Smartsheet workspace, converts each sheet to a markdown string, and stores it in MongoDB. This pre-populates the LLM context cache so the agent can answer questions without live API calls. |

---

### `scripts/`
One-off utility and operational scripts. Not part of the web application runtime.

| File | Purpose |
|------|---------|
| `generate_mmi_alerts.py` | Generates MMI project alerts and optionally writes them to MongoDB or Smartsheet. |
| `export_mmi_alerts_to_csv.py` | Exports alert data to CSV for review outside the system. |
| `dryrun_mmi_sync.py` | Dry-run version of the Smartsheet sync — logs what would be synced without writing. |
| `find_budget_report.py` | Locates budget report sheets within a Smartsheet workspace by folder traversal. |
| `inspect_financial_section.py` | Reads a Smartsheet sheet into a DataFrame and prints the financial section for debugging. |
| `list_folder_reports.py` | Lists all reports inside a Smartsheet folder. |
| `test_parse_mmi.py` | Tests the MMI Smartsheet parsing logic in isolation. |

---

### `tests/`
Integration and regression tests. Most tests make live API calls and are designed for manual execution rather than CI.

Key files include `test_financials.py`, `test_optics_update.py`, `test_smartsheet_upload.py`, `test_rally_data_fetch.py`, and others that validate specific integration points. `TIMEOUT_FIX_ANALYSIS.md` documents a resolved timeout issue.

---

### `documents/`
Runtime artifacts and static reference data.

| Path | Purpose |
|------|---------|
| `email_draft.json` | Template for AI-generated email drafts produced by the project agent. |
| `reports/` | CSV exports from Smartsheet — used as reference data for testing and debugging. Not committed as source of truth. |

The Excel project plan template (`GNP_Template_v4.xlsx`) is expected here at runtime (configured via `TEMPLATE_FILE` env var) but is not committed to the repository.

---

### `infrastructure/`
Kubernetes deployment manifests for OpenShift/UHG cloud.

| File | Purpose |
|------|---------|
| `deployment.yml` | Kubernetes `Deployment` manifest. Defines the pod spec, image reference (`APP_IMAGE_DETAIL`), environment injection from a ConfigMap and a Secret, resource limits, and liveness/readiness probes. Replicas, image, and deploy date are templated via CI/CD variable substitution. |
| `service.yml` | Kubernetes `Service` manifest. Exposes the application pod on a stable cluster-internal DNS name and port. |
| `dev-params.properties` | CI/CD pipeline parameter file for the development environment. Contains variable values (app name, namespace, image tag, etc.) used during deployment templating. |

---

### `archive/`
Deprecated code retained for reference.

These are older versions of the data wrappers and plan builders (Rally, Aha, Smartsheet, mapping) that were superseded by the current implementations in `engine/` and `upload/`. Not imported anywhere in the active codebase.

---

## Root-Level Files

### `.env` / `credentials.env`
Not committed. Created locally by copying `env.template`. Supplies all secrets and runtime configuration (API keys, MongoDB URI, Smartsheet workspace ID, etc.) to both the application and Docker. `config.py` reads these via `os.getenv()`.

### `env.template`
The committed reference file showing every environment variable the system expects, with placeholder values. This is the source of truth for what needs to be populated before running.

Key variable groups:
- **API Keys** — Aha, Smartsheet, Rally, Icarus, AccelQ
- **Service URLs** — base URLs for each external API
- **App Config** — host/port for FastAPI and Streamlit
- **Workspace IDs** — Smartsheet workspace, Rally workspace/project
- **MongoDB** — connection URI, credentials, database/collection names
- **Defaults** — BDL/RDL names, business owner, UI button color

### `config.py`
Central configuration class (`Config`). Reads all environment variables and exposes them as class attributes. Provides helper methods like `get_smartsheet_headers()` and `get_aha_headers()` so every module gets consistent, pre-built auth headers without duplicating logic.

### `requirements.txt`
Python dependencies. Key packages:
- `fastapi` + `uvicorn` — API server
- `streamlit` — frontend UI
- `langchain` + `langchain-openai` + `langgraph` — LLM agent framework
- `pymongo` — MongoDB client
- `pandas` + `numpy` + `openpyxl` — data processing and Excel handling
- `smartsheet-python-sdk` — Smartsheet API client (also used alongside raw `requests`)
- `requests` + `certifi` — HTTP calls to Aha, Rally, Icarus

### `Dockerfile`
Builds the production container image from UHG's internal golden Python 3.11 base image. Steps:
1. Sets `/app` as working directory.
2. Installs Python dependencies from `requirements.txt`.
3. Copies the full project into the image.
4. Makes `run.sh` executable.
5. Exposes port 8080.
6. Launches both FastAPI (on `127.0.0.1:8000`) and Streamlit (on `0.0.0.0:8080`) in the same container via a shell `CMD`.

### `docker-compose.yml`
Production Docker Compose config. Builds from the local `Dockerfile`, exposes ports 8080 and 8501, mounts `./documents` and `./upload` as volumes for data persistence, and injects all environment variables from `credentials.env`.

### `docker-compose.dev.yml`
Development variant. Adds live code-mounting so local file changes reflect inside the container without a rebuild. Enables hot-reload for both FastAPI (`--reload`) and Streamlit.

### `run.sh`
Local development entrypoint (outside Docker). Activates the local virtualenv (`.venv` or `venv`), then starts FastAPI on `127.0.0.1:8000` in the background and Streamlit in the foreground. Ports and hosts are configurable via environment variables.

---

## Data Flow Summary

```
User (Streamlit UI)
       │ HTTP POST /chat
       ▼
FastAPI (app/routes.py)
       │
       ├─── Plan Build ──► engine/mapping.py ──► Aha API, Icarus API (Rally + Optics)
       │                         │
       │                         ▼
       │                   pandas DataFrame
       │                         │
       │                         ▼
       │              upload/smartsheet_export.py ──► Smartsheet (new sheet)
       │
       ├─── Update ──────► upload/update_smartsheet.py ──► Smartsheet (existing sheet)
       │
       └─── Chat/Query ──► agent/project_agent.py
                                 │
                                 ├── agent/llm_context_builder.py ──► MongoDB
                                 ├── agent/azure_llm.py ──► Azure OpenAI
                                 └── agent/prompts.py

MongoDB (engine/mongodb_helper.py)
  ├── plan_metadata collection — active project plans and Smartsheet sheet IDs
  └── gnp_financials collection — GNP financial sheet tracking (active flag, sheet ID, dates)

agent/sync_smartsheet_markdown.py (standalone cron/job)
  ──► Smartsheet workspace ──► MongoDB (stores markdown summaries for LLM context)

https://docs.github.com/en/enterprise-cloud@latest/authentication/authenticating-with-single-sign-on/authorizing-a-personal-access-token-for-use-with-single-sign-on?utm_source=chatgpt.com

```
