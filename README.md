python -c "import config; print('DB_PORT:', config.DB_PORT); print('DB_USER configured:', bool(config.DB_USER)); print('ALPHA_DBS keys:', list(config.ALPHA_DBS.keys()))"
