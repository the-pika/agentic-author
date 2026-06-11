import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    
    print("🔍 Fetching available models using google-genai SDK...")
    try:
        # Use the new SDK's method to list models
        models = client.models.list()
        for m in models:
            # Check for embedding capability
            # Note: In the new SDK, supported_actions or similar might be used
            # For now, let's just print everything to see what's there
            print(f"Model: {m.name} | Display Name: {m.display_name}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_models()
