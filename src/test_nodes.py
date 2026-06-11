import os
import sys
from dotenv import load_dotenv

# Add src to python path to resolve imports
sys.path.append(os.path.join(os.path.dirname(__file__)))

from state import AgentState
from graph import (
    discovery_node, 
    strategist_node, 
    researcher_node, 
    distiller_node, 
    writer_node, 
    critic_node, 
    publisher_node,
    app
)

load_dotenv()

def test_full_node_suite():
    print("🧪 --- STARTING COMPREHENSIVE NODE TESTING --- 🧪\n")
    
    # Initialize state with mandatory fields
    state = AgentState(
        topic="Self-Correction in LLM Agents",
        niche="Artificial Intelligence",
        style="Technical & Rigorous"
    )

    # 1. Test Discovery
    print("📍 [1/7] Testing Discovery Node...")
    try:
        disc_upd = discovery_node(state)
        state.suggested_topics = disc_upd.get("suggested_topics", [])
        print(f"✅ Success: Generated {len(state.suggested_topics)} suggested topics.\n")
    except Exception as e:
        print(f"❌ Discovery Error: {e}")

    # 2. Test Strategist
    print("📍 [2/7] Testing Strategist Node...")
    try:
        strat_upd = strategist_node(state)
        state.content_plan = strat_upd.get("content_plan", "")
        state.topic = strat_upd.get("topic", state.topic)
        print(f"✅ Success: Plan generated for topic: '{state.topic}'\n")
    except Exception as e:
        print(f"❌ Strategist Error: {e}")

    # 3. Test Researcher
    print("📍 [3/7] Testing Researcher Node...")
    try:
        res_upd = researcher_node(state)
        state.research_notes = res_upd.get("research_notes", [])
        print(f"✅ Success: Gathered {len(state.research_notes)} research source entries.\n")
    except Exception as e:
        print(f"❌ Researcher Error: {e}")

    # 4. Test Distiller
    print("📍 [4/7] Testing Distiller Node...")
    try:
        dist_upd = distiller_node(state)
        state.summary_sheet = dist_upd.get("summary_sheet", "")
        print(f"✅ Success: Compressed notes into Technical Fact Sheet ({len(state.summary_sheet)} chars).\n")
    except Exception as e:
        print(f"❌ Distiller Error: {e}")

    # 5. Test Writer
    print("📍 [5/7] Testing Writer Node...")
    try:
        writer_upd = writer_node(state)
        state.draft = writer_upd.get("draft", "")
        print(f"✅ Success: Draft created ({len(state.draft)} chars).\n")
    except Exception as e:
        print(f"❌ Writer Error: {e}")

    # 6. Test Critic
    print("📍 [6/7] Testing Critic Node...")
    try:
        critic_upd = critic_node(state)
        state.critique = critic_upd.get("critique", "")
        status = "PASSED" if not state.critique else "FEEDBACK GIVEN"
        print(f"✅ Success: Review finished. Status: {status}\n")
    except Exception as e:
        print(f"❌ Critic Error: {e}")

    # 7. Test Publisher
    print("📍 [7/7] Testing Publisher Node...")
    try:
        pub_upd = publisher_node(state)
        print(f"✅ Success: Metadata extracted. Title: {pub_upd.get('content_plan')}\n")
    except Exception as e:
        print(f"❌ Publisher Error: {e}")

    print("🏁 --- INDIVIDUAL NODE TESTING COMPLETE --- 🏁\n")

def test_graph_e2e():
    print("🔄 --- TESTING END-TO-END GRAPH EXECUTION --- 🔄")
    try:
        # Using a very specific topic to ensure speed
        inputs = {"topic": "Agentic Workflows in LangGraph", "niche": "AI Engineering"}
        # Limit recursion to avoid long runs during test
        result = app.invoke(inputs, config={"recursion_limit": 15})
        
        if result.get("draft"):
            print("✅ Graph E2E: Final draft generated successfully.")
            print(f"📊 Revisions: {result.get('revision_count')}")
        else:
            print("❌ Graph E2E: No draft found in final state.")
            
    except Exception as e:
        print(f"❌ Graph E2E Error: {e}")

if __name__ == "__main__":
    test_full_node_suite()
    test_graph_e2e()
