# Environment Variables Template
# Copy this file to credentials.env and fill in your actual values

# API Keys (Required)
AHA_API_KEY=Bearer your_aha_api_key_here
ICARUS_API_KEY=your_icarus_api_key_here
SMARTSHEET_API_KEY=your_smartsheet_api_key_here
RALLY_API_KEY=your_rally_api_key_here
ACCELQ_API_KEY=your_accelq_api_key_here

# Service URLs (Optional - defaults provided)
RALLY_URL=https://rally1.rallydev.com/slm/webservice/v2.0
AHA_BASE_URL=https://optum.aha.io/api/v1
SMARTSHEET_BASE_URL=https://api.smartsheet.com/2.0
ICARUS_BASE_URL=https://insights.hcp.uhg.com/api/icarus/v1

# Application Configuration
API_HOST=127.0.0.1
API_PORT=8000
STREAMLIT_HOST=0.0.0.0
STREAMLIT_PORT=8080
API_BASE_URL=http://127.0.0.1:8000

# Workspace and Project Configuration
RALLY_WORKSPACE=UHG
RALLY_PROJECT=Pioneers GenAI
SMARTSHEET_WORKSPACE_ID=your_workspace_id_here

# File Paths
METADATA_FILE=documents/plan_metadata.json
TEMPLATE_FILE=documents/GNP_Template_v4.xlsx

# Default Values
DEFAULT_BDL=Jason Merckling
DEFAULT_RDL=Chris Capewell
DEFAULT_BUSINESS_OWNER=Gina Milana

# UI Configuration
BUTTON_COLOR=#001f3f

# Request Settings
REQUEST_TIMEOUT=180

# SSL Configuration (set to false for corporate environments)
VERIFY_SSL=false

# MongoDB Configuration
MONGODB_URI=mongodb://mongodb-service:27017
MONGODB_USERNAME=adminUser
MONGODB_PASSWORD=securePassword
MONGODB_DATABASE=project_plans
MONGODB_COLLECTION=plan_metadata
