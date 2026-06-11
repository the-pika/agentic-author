import os
from dotenv import load_dotenv
from graph import app
from memory_manager import BlogMemory
from state import AgentState

load_dotenv()

def run_test_research():
    print("🚀 --- STARTING END-TO-END FLOW VERIFICATION --- 🚀\n")
    
    # 1. Initialize State
    initial_state = {
        "topic": "The Future of LangGraph in 2026",
        "revision_count": 0
    }
    
    # 2. Run the Graph
    print(f"Target Topic: {initial_state['topic']}\n")
    
    try:
        # We invoke the compiled app
        final_state = app.invoke(initial_state)
        
        print("\n✅ --- FLOW COMPLETED SUCCESSFULLY --- ✅")
        
        # 3. Verify Draft Output
        print("\n--- FINAL DRAFT PREVIEW ---")
        draft = final_state.get('draft', '')
        if draft:
            # Print first 500 chars to avoid flooding terminal
            print(draft[:500] + "...")
        else:
            print("❌ Error: No draft generated!")

        # 4. Verify Revision Count
        print(f"\nRevision Count: {final_state.get('revision_count', 0)}")

        # 5. Verify Memory Storage
        print("\n--- VERIFYING MEMORY STORAGE ---")
        memory = BlogMemory()
        history = memory.search_history("LangGraph")
        print("Latest entries in Memory:")
        print(history)

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR DURING FLOW: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test_research()
