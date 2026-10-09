Select-String -Path .\group_validator.py,.\member_validator.py -Pattern "get_conn\(|q\(|ALPHA_DBS|ERQQ_DB|ERQQ_HOST" -Context 1,2
