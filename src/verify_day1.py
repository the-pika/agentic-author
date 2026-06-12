from dotenv import load_dotenv
from state import AgentState
from llm_config import get_model
from memory_manager import BlogMemory
from graph import app

load_dotenv()

def verify():
    print("🔍 Starting Day 1 Verification...")
    
    # 1. Check State
    try:
        _ = AgentState(topic="AI Agents", research_notes=["Result 1"], revision_count=0)
        print("✅ State Schema: Valid")
    except Exception as e:
        print(f"❌ State Schema Error: {e}")

    # 2. Check Database
    try:
        _ = BlogMemory()
        print("✅ ChromaDB Connection: Valid")
    except Exception as e:
        print(f"❌ Database Error: {e} (Check if 'chromadb' is installed)")

    # 3. Check LLM Config
    try:
        model = get_model()
        # Use .model attribute which is standard for ChatGoogleGenerativeAI
        model_name = getattr(model, "model", "Unknown")
        print(f"✅ Gemini Model Init: Valid (Model: {model_name})")
    except Exception as e:
        print(f"❌ LLM Config Error: {e}")

    # 4. Check Graph Compilation
    try:
        print("✅ LangGraph Compilation: Valid")
        # Print nodes to verify skeleton
        print(f"Nodes detected: {app.nodes.keys()}")
    except Exception as e:
        print(f"❌ Graph Error: {e}")

if __name__ == "__main__":
    verify()