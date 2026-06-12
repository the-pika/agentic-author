import streamlit as st
import sys
import os
import pandas as pd
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from graph import app, memory  # noqa: E402
from state import AgentState  # noqa: E402
from llm_config import handle_error  # noqa: E402

# Page Configuration
st.set_page_config(page_title="Agentic Author", layout="wide")

# Custom CSS for premium enterprise design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Global Typography & Background */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #2D3748;
    }
    
    /* Fix for expander arrow overlap text */
    [data-testid="stExpander"] svg, [data-testid="stExpander"] [data-testid="stIcon"] {
        display: none !important;
        visibility: hidden !important;
    }
    [data-testid="stExpander"] p {
        font-size: 0.9rem !important;
    }

    .stApp {
        background-color: #F7FAFC; /* Soft light background */
    }

    /* H1, H2, H3 Hierarchy */
    h1 {
        font-weight: 700 !important;
        color: #1A202C !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem !important;
    }
    
    .subheading {
        font-size: 0.95rem;
        color: #718096;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #E1E8F0 !important; /* Dominant color */
        border-right: 1px solid #CBD5E0;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        padding-top: 1rem;
    }

    /* Card Containers / Lifted Effect */
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }
    
    /* Expander / Knowledge Vault Styling */
    .stExpander {
        background-color: white !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }

    /* Buttons - Secondary Color #6ED3CF and Accent #9068BE */
    .stButton > button {
        width: 100%;
        background-color: #6ED3CF !important; /* Secondary */
        color: #1A202C !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.75rem !important;
    }
    
    .stButton > button:hover {
        background-color: #9068BE !important; /* Accent */
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(144, 104, 190, 0.3) !important;
    }

    /* Input Fields */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important;
    }
    
    /* Data Presentation (Tables) */
    [data-testid="stTable"], [data-testid="stDataFrame"] {
        border: none !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #E1E8F0;
        border-radius: 8px 8px 0 0;
        border: none;
        color: #4A5568;
        font-weight: 600;
        padding: 0 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #9068BE !important;
        border-bottom: 2px solid #9068BE !important;
    }

    /* Spacing fixes */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
        max-width: 1200px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Agentic Author")
st.markdown("<p class='subheading'>Autonomous Research and Writing Agent</p>", unsafe_allow_html=True)
st.markdown("---")

# Initialize Session State
if "final_draft" not in st.session_state: st.session_state.final_draft = ""
if "all_research" not in st.session_state: st.session_state.all_research = []
if "critique_history" not in st.session_state: st.session_state.critique_history = []
if "metadata" not in st.session_state: st.session_state.metadata = {"title": "", "summary": "", "references": []}
if "selected_topic" not in st.session_state: st.session_state.selected_topic = ""
if "suggestions" not in st.session_state: st.session_state.suggestions = []
if "last_niche" not in st.session_state: st.session_state.last_niche = ""
if "last_run_time" not in st.session_state: st.session_state.last_run_time = 0

# Sidebar: User Profile & Controls
with st.sidebar:
    st.header("🔑 API Configuration")
    google_key = st.text_input("Google Gemini API Key", type="password", help="Enter your Gemini 1.5 API Key")
    tavily_key = st.text_input("Tavily API Key", type="password", help="Enter your Tavily API Key")
    
    st.markdown("---")
    st.header("📋 Project Settings")
    
    niche = st.text_input("Research Niche", value="Artificial Intelligence", help="e.g., Quantum Computing, Sustainable Energy")
    style = st.selectbox("Writing Style", [
        'Paper-to-Practice', 
        'First-Principles Explainer', 
        'Production Deep-Dive', 
        'Architectural Opinionated', 
        'Executive Summary'
    ], index=0)

    st.markdown("---")
    st.header("Research Settings")
    topic = st.text_input("Blog Topic", value=st.session_state.selected_topic, placeholder="Enter topic or brainstorm...")
    max_revisions = st.slider("Max Revisions", 1, 3, 2)
    
    col_a, col_b = st.columns(2)
    with col_a:
        brainstorm_btn = st.button("Brainstorm")
    with col_b:
        start_btn = st.button("Start")

    if brainstorm_btn:
        if not google_key:
            st.error("Please provide a Google API Key.")
        else:
            with st.spinner("Brainstorming topics..."):
                try:
                    from graph import discovery_node
                    mock_state = AgentState(niche=niche, topic="", google_api_key=google_key)
                    result = discovery_node(mock_state)
                    st.session_state.suggestions = result.get("suggested_topics", [])
                    st.success("Topics generated!")
                except Exception as e:
                    st.error(handle_error(e))

    if st.session_state.suggestions:
        st.markdown("---")
        st.session_state.selected_topic = st.radio(
            "Select a Suggested Topic:",
            options=st.session_state.suggestions,
            index=None if not st.session_state.selected_topic else st.session_state.suggestions.index(st.session_state.selected_topic) if st.session_state.selected_topic in st.session_state.suggestions else None
        )

# Main Layout
col_logs, col_output = st.columns([1, 1.5])

with col_logs:
    st.subheader("Agent Activity")
    
    # Visual Memory: Knowledge Vault
    with st.expander("Knowledge Vault (Past Blogs)", expanded=False):
        try:
            coll = memory.vectorstore.get()
            if coll and coll['metadatas']:
                df = pd.DataFrame(coll['metadatas'])
                st.dataframe(df[['title', 'summary']], use_container_width=True, hide_index=True)
            else:
                st.info("Vault is empty.")
        except Exception as e:
            st.error(f"Vault error: {e}")

    log_container = st.container()

with col_output:
    st.subheader("Research Output")
    output_area = st.empty()
    
    if st.session_state.final_draft:
        output_area.markdown(st.session_state.final_draft)
        
        st.markdown("---")
        if st.button("Confirm Publication & Save"):
            with st.spinner("Saving to Academic Library..."):
                try:
                    # Save Blog Post using the new save_blog method
                    memory.save_blog(
                        title=st.session_state.metadata["title"],
                        content=st.session_state.final_draft,
                        short_summary=st.session_state.metadata["summary"]
                    )
                    # Save References
                    memory.save_references(
                        blog_title=st.session_state.metadata["title"],
                        refs_list=st.session_state.metadata["references"]
                    )
                    st.success("Successfully published to ChromaDB!")
                    st.balloons()
                except Exception as e:
                    st.error(handle_error(e))

# Logic Execution
if start_btn:
    # 1. Validation
    active_topic = topic if topic else st.session_state.selected_topic
    current_time = time.time()
    cooldown = 60 # seconds
    
    if not google_key or not tavily_key:
        st.warning("Please provide both API Keys in the sidebar.")
    elif not active_topic:
        st.warning("Please provide a topic.")
    elif current_time - st.session_state.last_run_time < cooldown:
        wait_time = int(cooldown - (current_time - st.session_state.last_run_time))
        st.warning(f"Please wait {wait_time} seconds before starting another research task.")
    else:
        st.session_state.last_run_time = current_time
        st.session_state.final_draft = ""
        st.session_state.all_research = []
        st.session_state.critique_history = []
        
        with log_container:
            with st.status("Orchestrating Research Agents...", expanded=True) as status:
                try:
                    initial_state = {
                        "topic": active_topic, 
                        "niche": niche, 
                        "style": style, 
                        "revision_count": 0,
                        "google_api_key": google_key,
                        "tavily_api_key": tavily_key
                    }
                    
                    for event in app.stream(initial_state, config={"recursion_limit": 25}):
                        for node, output in event.items():
                            if node == "discovery": 
                                with st.chat_message("discovery"):
                                    st.write("**Discovery Agent:** Checking niche alignment and trending angles...")
                            
                            elif node == "strategist": 
                                with st.chat_message("strategist"):
                                    st.write("**Strategist Agent:** Developing content plan and research queries...")
                            
                            elif node == "researcher": 
                                with st.chat_message("researcher"):
                                    st.write("**Researcher Agent:** Fetching data from Arxiv and Tavily...")
                                    if "research_notes" in output: 
                                        st.session_state.all_research.extend(output["research_notes"])
                                        with st.expander("View Raw Findings"):
                                            for note in output["research_notes"]:
                                                st.caption(note[:200] + "...")
                            
                            elif node == "distiller": 
                                with st.chat_message("distiller"):
                                    st.write("**Distiller Agent:** Synthesizing notes into a technical Fact Sheet...")
                            
                            elif node == "writer": 
                                with st.chat_message("writer"):
                                    st.write(f"**Writer Agent:** Drafting the post in **{style}** style...")
                                if "draft" in output: 
                                    st.session_state.final_draft = output["draft"]
                            
                            elif node == "critic":
                                crit = output.get("critique", "")
                                if crit:
                                    with st.chat_message("critic"):
                                        st.warning("**Critic Agent:** Revision requested. Sending feedback to Writer.")
                                    st.session_state.critique_history.append(crit)
                                else: 
                                    with st.chat_message("critic"):
                                        st.success("**Critic Agent:** Quality check passed!")
                            
                            elif node == "publisher":
                                with st.chat_message("publisher"):
                                    st.write("**Publisher Agent:** Finalizing title and metadata...")
                                st.session_state.metadata["title"] = output.get("topic", "Untitled")
                                st.session_state.metadata["summary"] = output.get("short_summary", "No summary")
                                st.session_state.metadata["references"] = output.get("references", [])

                    status.update(label="Research Phase Complete", state="complete", expanded=False)
                    output_area.markdown(st.session_state.final_draft)
                    st.rerun()

                except Exception as e:
                    status.update(label="Workflow Failed", state="error")
                    st.error(handle_error(e))

# Bottom Tabs
st.markdown("---")
tab_res, tab_crit, tab_mem = st.tabs(["Research Data", "Critique History", "Project Memory"])

with tab_res:
    if st.session_state.all_research:
        for idx, note in enumerate(st.session_state.all_research):
            with st.expander(f"Dataset {idx+1}"): st.write(note)
    else: st.info("No research data yet.")

with tab_crit:
    if st.session_state.critique_history:
        for idx, feedback in enumerate(st.session_state.critique_history):
            st.info(f"**Revision {idx+1}:**\n\n{feedback}")
    else: st.info("No critiques recorded.")

with tab_mem:
    st.subheader("Blog History")
    try:
        coll = memory.vectorstore.get()
        if coll and coll['metadatas']:
            df = pd.DataFrame(coll['metadatas'])
            st.dataframe(df[['title', 'summary']], use_container_width=True)
        else:
            st.info("No blogs found in memory.")
    except Exception as e:
        st.error(f"Could not load blog memory: {e}")
        
    st.subheader("Academic References")
    try:
        ref_coll = memory.ref_store.get()
        if ref_coll and ref_coll['metadatas']:
            ref_df = pd.DataFrame(ref_coll['metadatas'])
            # Filter columns to show relevant ones
            cols = ['blog_link', 'title', 'author', 'url']
            available_cols = [c for c in cols if c in ref_df.columns]
            st.dataframe(ref_df[available_cols], use_container_width=True)
        else:
            st.info("No references found in memory.")
    except Exception as e:
        st.error(f"Could not load reference memory: {e}")
