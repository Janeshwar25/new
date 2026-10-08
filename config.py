# ACCELQ Configuration
LOGIN_URL = "https://optum.accelq.io"
TENANT = "optum"
PROJECT = "Optum_USP_Product_Ecosystem"
USER_ID = "janeshwar_chowdhary@optum.com"
API_KEY = "eELJvWps9t88lQ58ew4Z6nmKJ3NT0v_oOc_YWbiYW04"



# ============================================
# Cirrus MySQL DB Configuration (GCP Auth)
# ============================================
import subprocess
import time

# Common credentials
DB_USER = "janeshwar_chowdhary"
DB_PORT = 3306

# Master Databases (5 instances)
ALPHA_DBS = {
    "aquarius_tent01": {
        "host": "172.19.96.239",
        "database": "tent01"
    },
    "memb01": {
        "host": "172.19.96.235",
        "database": "memb01"
    },
    "membergroup": {
        "host": "172.19.96.236",
        "database": "membergroup"
    },
    "rso_01": {
        "host": "172.19.96.238",
        "database": "rso_01"
    },
    "tent01_bootes": {
        "host": "172.19.96.240",
        "database": "tent01"
    }
}

# Smart Token Manager (Auto-refresh)
class TokenManager:
    """Manages GCP OAuth token with auto-refresh"""
    
    def __init__(self):
        self.token = None
        self.expiry_time = 0
    
    def get_token(self):
        # Return cached token if still valid
        if self.token and time.time() < self.expiry_time:
            return self.token
        
        # Fetch fresh token from gcloud
        try:
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                shell=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"gcloud error: {result.stderr}")
            
            self.token = result.stdout.strip()
            # Cache for 50 minutes (token valid 1 hour)
            self.expiry_time = time.time() + (50 * 60)
            print("✅ Fresh GCP token obtained")
            return self.token
            
        except Exception as e:
            print(f"❌ Token error: {e}")
            return None

# Single global instance (reuse across scripts)
token_manager = TokenManager()

# Function to get DB password (auto-fresh token)
def get_db_password():
    return token_manager.get_token()