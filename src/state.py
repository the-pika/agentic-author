from typing import Annotated
from pydantic import BaseModel, Field
import operator

class AgentState(BaseModel):
    """
    Represents the state of the research and writing process.
    Uses Pydantic BaseModel for validation and type safety.
    """
    topic: str = ""
    history_context: str = ""
    research_notes: Annotated[list[str], operator.add] = Field(default_factory=list)
    content_plan: str = ""
    draft: str = ""
    critique: str = ""
    revision_count: int = 0
    
    # New Fields for Academic & Personalization
    niche: str = ""
    style: str = ""
    summary_sheet: str = ""
    short_summary: str = ""
    references: Annotated[list[dict], operator.add] = Field(default_factory=list)
    suggested_topics: list[str] = Field(default_factory=list)
    
    # BYOK Keys
    google_api_key: str = ""
    tavily_api_key: str = ""
