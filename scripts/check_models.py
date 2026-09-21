from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

try:
    models = client.models.list()
    for m in models:
        print(f"Model ID: {m.name} - Version: {getattr(m, 'version', 'N/A')}")
except Exception as e:
    print(f"Error listing models: {e}")
