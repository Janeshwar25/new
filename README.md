Select-String -Path .\group_validator.py,.\member_validator.py -Pattern "get_conn(","q(","ALPHA_DBS","ERRQ_DB","ERRQ_HOST" -SimpleMatch -Context 1,2
