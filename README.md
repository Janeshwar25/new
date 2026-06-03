from dotenv import load_dotenv
import os

load_dotenv("credentials.env")

print(os.getenv("GROQ_API_KEY"))
