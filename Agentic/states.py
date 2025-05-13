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
    is_context_enough : str
    is_wiki_enough : Optional[str]=None


class State(BaseModel):
    """Simple state object."""
    # user
    session_id : str
    msg : List[str]

    input_type: Optional[Literal["image", "text"]]

    content : Optional[str] = None
    image_bytes : Optional[str] = None
    # context
    product_info : Optional[VlmResponse] = None
    # routing
    workflow : Optional[RouterResponse] = None
    routing : Optional[Wiki_routing] = None
    # llm resps
    wiki_response : Optional[str] = None
    wiki_data : Optional[str] = None
    links : Optional[List[Dict]] = None
    # image_detection : Optional[bool] = False
