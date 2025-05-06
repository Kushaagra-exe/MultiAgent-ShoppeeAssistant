from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
from typing import Optional, Literal, List
from datetime import datetime
from typing_extensions import Literal, Dict



class VlmResponse(BaseModel):
    description : Dict
    product_details : Dict


class RouterResponse(BaseModel):
    tool_usage: Literal["Wiki_tool", "links_tool", "no_tool"] = Field(description="The tool to be used by the LLM based on user's request. It must be one of: 'links_tool' or 'Wiki_tool'")

class Wiki_routing(BaseModel):
    is_context_enough : bool
    is_wiki_enough : bool


class State(BaseModel):
    """Simple state object."""
    msg : List[str]
    input_type: Literal["image", "text"]
    content : str
    image_bytes : bytes
    product_info : VlmResponse
    workflow : RouterResponse
    wiki_response : str
    wiki_data : str
    session_id : str
    links : List[Dict]
    routing : Wiki_routing
