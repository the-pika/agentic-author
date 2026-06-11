import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun

# Load environment variables
load_dotenv()

def get_search_tool(api_key: str = None) -> TavilySearchResults:
    """
    Initializes and returns the Tavily search tool.
    """
    api_key = api_key or os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found. Please ensure it is set in your .env file or provided via UI.")
        
    return TavilySearchResults(max_results=5, tavily_api_key=api_key)

def get_arxiv_tool() -> ArxivQueryRun:
    """
    Initializes and returns the Arxiv search tool.
    """
    return ArxivQueryRun()
