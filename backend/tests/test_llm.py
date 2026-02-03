import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-flash-latest"
print(f"Testing model: {MODEL_NAME}...")

try:
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content("Hello, are you working fast?")
    print(f"✅ Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
