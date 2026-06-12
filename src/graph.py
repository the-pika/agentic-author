from typing import Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState
from llm_config import get_model
from memory_manager import BlogMemory
from tools import get_search_tool, get_arxiv_tool
from prompts import (
    DISCOVERY_PROMPT,
    STRATEGIST_SYSTEM_PROMPT,
    RESEARCHER_QUERY_PROMPT,
    RESEARCHER_SUMMARY_PROMPT,
    DISTILLER_SYSTEM_PROMPT,
    WRITER_STYLE_INSTRUCTIONS,
    WRITER_SYSTEM_PROMPT,
    CRITIC_SYSTEM_PROMPT,
    PUBLISHER_EXTRACTION_PROMPT
)

# Initialize memory (Shared resource, does not depend on LLM keys)
memory = BlogMemory()

# Helper to get model from state
def _get_model(state: AgentState):
    return get_model(api_key=state.google_api_key)

# Node Definitions
def discovery_node(state: AgentState) -> dict:
    """
    Discovery node: Suggests trending topics based on history, niche, and reference library.
    """
    print("--- DISCOVERY: Generating topic suggestions ---")
    model = _get_model(state)
    
    # 1. Get History and Reference Context
    # Using get_recent_summaries to get a broader view of past work
    history = memory.get_recent_summaries(limit=10)
    ref_context = memory.get_reference_context(limit=10)
    
    # 2. Generate Topics
    prompt = DISCOVERY_PROMPT.format(
        niche=state.niche,
        history=history,
        ref_context=ref_context
    )
    
    response = model.invoke([HumanMessage(content=prompt)])
    content = response.content
    if isinstance(content, list):
        content = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
        
    topics = [t.strip() for t in content.split("\n") if t.strip()]
    
    return {"suggested_topics": topics[:5]}

def strategist_node(state: AgentState) -> dict:
    """
    Strategist node: Plans the content based on the topic and historical context.
    Generates academic-focused research queries.
    """
    model = _get_model(state)
    # If no topic is provided but we have suggestions, pick the first one
    current_topic = state.topic
    if not current_topic and state.suggested_topics:
        current_topic = state.suggested_topics[0]
        print(f"--- STRATEGIST: No topic provided. Selecting suggestion: '{current_topic}' ---")
    else:
        print(f"--- STRATEGIST: Planning for topic '{current_topic}' ---")

    # 1. Get Historical Context
    history = memory.search_history(current_topic)

    # 2. Generate Content Plan using Gemini
    system_prompt = STRATEGIST_SYSTEM_PROMPT

    user_prompt = f"Topic: {current_topic}\n\nPast History:\n{history}"

    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    content = response.content
    if isinstance(content, list):
        content = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])

    return {
        "topic": current_topic,
        "history_context": history,
        "content_plan": content
    }


def researcher_node(state: AgentState) -> dict:
    """
    Researcher node: Performs academic research primarily using Arxiv.
    """
    print("--- RESEARCHER: Gathering academic information ---")
    model = _get_model(state)
    search_tool = get_search_tool(api_key=state.tavily_api_key)
    arxiv_tool = get_arxiv_tool()
    
    # 1. Extract search queries from content_plan using Gemini
    query_prompt = RESEARCHER_QUERY_PROMPT.format(content_plan=state.content_plan)
    
    query_response = model.invoke([HumanMessage(content=query_prompt)])
    content = query_response.content
    if isinstance(content, list):
        content = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
    
    queries = [q.strip() for q in content.split("\n") if q.strip()]
    
    # 2. Execute searches and summarize facts
    all_facts = []
    for query in queries:
        print(f"Searching Arxiv for: {query}")
        try:
            # Primary: Arxiv
            search_results = arxiv_tool.invoke(query)
            
            # Fallback to Tavily if Arxiv is sparse
            if not search_results or len(search_results) < 50:
                print(f"Sparse results on Arxiv, trying Tavily for: {query}")
                search_results = search_tool.invoke(query)
            
            # Summarize results into facts using Gemini
            summary_prompt = RESEARCHER_SUMMARY_PROMPT.format(
                query=query,
                search_results=search_results
            )
            
            summary_response = model.invoke([HumanMessage(content=summary_prompt)])
            s_content = summary_response.content
            if isinstance(s_content, list):
                s_content = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in s_content])
                
            all_facts.append(f"Source Data for '{query}':\n{s_content}")
        except Exception as e:
            print(f"⚠️ Search failed for query '{query}': {e}")
            all_facts.append(f"Search failed for '{query}': {e}")

    return {
        "research_notes": all_facts
    }

def distiller_node(state: AgentState) -> dict:
    """
    Distiller node: Compresses raw research notes into a technical summary sheet.
    """
    print("--- DISTILLER: Compressing research into a Fact Sheet ---")
    model = _get_model(state)
    
    raw_notes = "\n\n".join(state.research_notes)
    
    prompt = DISTILLER_SYSTEM_PROMPT
    
    response = model.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=raw_notes)
    ])
    
    content = response.content
    if isinstance(content, list):
        content = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
        
    return {"summary_sheet": content}

def writer_node(state: AgentState) -> dict:
    """
    Writer node: Drafts a highly technical academic blog post using the summary sheet.
    Persona: Senior AI Research Engineer.
    """
    print(f"--- WRITER: Crafting the technical blog post in '{state.style}' style ---")
    model = _get_model(state)

    # Fallback to a default if style isn't recognized
    specific_instruction = WRITER_STYLE_INSTRUCTIONS.get(state.style, "Maintain a balanced, highly technical perspective.")

    system_prompt = WRITER_SYSTEM_PROMPT.format(
        style=state.style,
        specific_instruction=specific_instruction
    )

    user_prompt = (
        f"Topic: {state.topic}\n\n"
        f"Content Plan:\n{state.content_plan}\n\n"
        f"Technical Fact Sheet:\n{state.summary_sheet}\n\n"
        f"Previous Critique (if any):\n{state.critique}\n\n"
        "Please write the full technical blog post in Markdown format."
    )

    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    content = response.content
    if isinstance(content, list):
        content = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])

    return {
        "draft": content
    }

def critic_node(state: AgentState) -> dict:
    """
    Critic node: Reviews the draft based on the summary sheet and technical rigor.
    """
    print("--- CRITIC: Reviewing the draft ---")
    model = _get_model(state)

    system_prompt = CRITIC_SYSTEM_PROMPT

    user_prompt = (
        f"Technical Fact Sheet:\n{state.summary_sheet}\n\n"
        f"Draft:\n{state.draft}"
    )

    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    critique = response.content
    if isinstance(critique, list):
        critique = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in critique])

    if critique.strip().upper() == "PASSED":
        return {"critique": ""}
    
    return {
        "critique": critique,
        "revision_count": state.revision_count + 1
    }

def publisher_node(state: AgentState) -> dict:
    """
    Publisher node: Finalizes the blog and returns metadata for manual saving.
    Generates a 4-5 line summary for the DB.
    """
    print("--- PUBLISHER: Finalizing draft metadata ---")
    model = _get_model(state)

    # 1. Extract Title, Summary, and References using Gemini
    extraction_prompt = PUBLISHER_EXTRACTION_PROMPT.format(draft=state.draft)

    response = model.invoke([HumanMessage(content=extraction_prompt)])
    content = response.content
    if isinstance(content, list):
        content = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])

    # Parse results
    title = ""
    summary = ""
    refs = []
    
    import json
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
        elif line.startswith("Summary:"):
            # Collect the summary which might be multi-line
            summary_lines = []
            summary_lines.append(line.replace("Summary:", "").strip())
            # Look ahead for references or other markers
            for next_line in lines[i+1:]:
                if next_line.startswith("References:"):
                    break
                if next_line.strip():
                    summary_lines.append(next_line.strip())
            summary = " ".join(summary_lines)
        elif line.startswith("References:"):
            json_str = line.replace("References:", "").strip()
            try:
                refs = json.loads(json_str)
            except Exception:
                print("⚠️ Failed to parse references JSON")

    # Fallback if parsing fails
    if not title:
        title = state.topic or "Untitled Post"
    if not summary:
        summary = f"A technical deep-dive into {state.topic}."

    return {
        "topic": title,
        "short_summary": summary,
        "references": refs
    }

# Conditional Edge Logic
def should_continue(state: AgentState) -> Literal["writer", "publisher"]:
    """
    Determines whether to loop back to the writer for revision or proceed to publication.
    """
    if state.critique.strip() and state.revision_count < 3:
        print(f"--- REVISING (Revision Count: {state.revision_count}) ---")
        return "writer"
    
    print("--- PROCEEDING TO PUBLISH ---")
    return "publisher"

# Graph Construction
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("discovery", discovery_node)
workflow.add_node("strategist", strategist_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("distiller", distiller_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)
workflow.add_node("publisher", publisher_node)

# Set Up Edges
workflow.add_edge(START, "discovery")
workflow.add_edge("discovery", "strategist")
workflow.add_edge("strategist", "researcher")
workflow.add_edge("researcher", "distiller")
workflow.add_edge("distiller", "writer")
workflow.add_edge("writer", "critic")

# Add Conditional Edge from Critic
workflow.add_conditional_edges(
    "critic",
    should_continue,
    {
        "writer": "writer",
        "publisher": "publisher"
    }
)

# Final Edge
workflow.add_edge("publisher", END)

# Compile the Graph
app = workflow.compile()
