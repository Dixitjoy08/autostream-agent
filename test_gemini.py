import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "API Key NOT found")

genai.configure(api_key=api_key)

print("\n📋 Available Gemini Models:")
print("="*60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")

print("="*60)