import shutil
import os

def reset_database():
    db_path = "./chroma_db"
    if os.path.exists(db_path):
        print(f"🗑️ Removing existing database at {db_path}...")
        try:
            shutil.rmtree(db_path)
            print("✅ Database cleared successfully!")
        except Exception as e:
            print(f"❌ Error removing database: {e}")
    else:
        print("ℹ️ No database found at ./chroma_db. Nothing to clear.")

if __name__ == "__main__":
    reset_database()
