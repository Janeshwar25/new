{
    "version": "0.2.0",
    "configurations": [
    {"name":"Python Debugger: Current File","type":"debugpy","request":"launch","program":"${file}","console":"integratedTerminal"},    {
            "name": "Run Streamlit App",
            "type": "python",
            "request": "launch",
            "module": "streamlit",
            "args": [
                "run",
                "app/app.py"
            ],
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Run FastAPI Backend",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.routes:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--reload"
            ],
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
