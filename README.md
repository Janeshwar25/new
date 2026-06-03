cd /Users/janeshwarchowdhary/Desktop/g
python3 -m uvicorn app.routes:app --host 127.0.0.1 --port 8000 --reload

cd /Users/janeshwarchowdhary/Desktop/g
PYTHONPATH=. streamlit run app/app.py
