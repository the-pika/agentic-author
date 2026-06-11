import chromadb
from chromadb.config import Settings

def polite_reset():
    db_path = "./chroma_db"
    print(f"🔄 Attempting to reset collections in {db_path}...")
    try:
        client = chromadb.PersistentClient(path=db_path)
        # List all collections
        collections = client.list_collections()
        for col in collections:
            print(f"🗑️ Deleting collection: {col.name}")
            client.delete_collection(col.name)
        print("✅ All collections cleared!")
    except Exception as e:
        print(f"❌ API Reset failed: {e}")
        print("💡 Tip: If the error is a 'WinError 32', please stop the Streamlit app and run this script again.")

if __name__ == "__main__":
    polite_reset()
