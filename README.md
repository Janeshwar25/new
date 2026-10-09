Select-String -Path .\member_validator.py -Pattern "def get_conn","ERRQ_HOST","ERRQ_DB","ALPHA_DBS","def q(","get_conn(db)" -SimpleMatch -Context 3,8
