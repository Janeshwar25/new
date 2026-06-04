cd Desktop\g
py -m uvicorn app.routes:app --host 127.0.0.1 --port 8000 --reload

cd Desktop\g
set PYTHONPATH=.
py -m streamlit run app/app.py
