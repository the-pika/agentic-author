from dotenv import load_dotenv
load_dotenv()

import os
import logging
import traceback
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("error.log"),
        logging.StreamHandler()
    ]
)
# Customizing console to be cleaner (only level and message)
console_formatter = logging.Formatter("%(levelname)s: %(message)s")
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
        handler.setFormatter(console_formatter)

def _get_api_key(provided_key: str = None) -> str:
    """Retrieves and validates the GOOGLE_API_KEY."""
    api_key = provided_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please ensure it is set in your .env file or provided via UI.")
    return api_key

def get_model(api_key: str = None) -> ChatGoogleGenerativeAI:
    """
    Initializes and returns the ChatGoogleGenerativeAI model.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=_get_api_key(api_key),
        temperature=0.7
    )

def get_embeddings(api_key: str = None) -> GoogleGenerativeAIEmbeddings:
    """
    Initializes and returns the GoogleGenerativeAIEmbeddings model.
    """
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        google_api_key=_get_api_key(api_key)
    )

def handle_error(e: Exception) -> str:
    """
    Logs the full traceback to error.log but returns a user-friendly string.
    """
    logging.error(f"Error captured: {e}")
    logging.error(traceback.format_exc())
    
    error_msg = str(e).lower()
    
    if "429" in error_msg or "quota" in error_msg:
        return "⚠️ LLM Quota reached. Please wait a minute before retrying."
    if "connection" in error_msg or "timeout" in error_msg:
        return "🔌 Connection error. Please check your internet."
    if "api_key" in error_msg:
        return "🔑 Invalid API Key. Check your .env file."
        
    return f"❌ An unexpected error occurred: {type(e).__name__}"
