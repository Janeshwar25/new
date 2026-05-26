cd Desktop\g
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.routes:app --host 127.0.0.1 --port 8000 --reload

cd Desktop\g
venv\Scripts\activate
set PYTHONPATH=.
streamlit run app/app.py

py -m uvicorn app.routes:app --host 127.0.0.1 --port 8000 --reload
