from pydantic import BaseModel
from langgraph.graph.message import add_messages
from typing_extensions import Annotated,TypedDict,List
from typing import Optional
import operator

class State(TypedDict):
    messages:Annotated[List[str],add_messages]
    image_path:Annotated[Optional[str],add_messages] 
    analysis_result:Optional[str]=None
    image_path_processed:Optional[bool]=None
    product_search_results:Optional[List[str]]=None
    product_search_intent:Optional[bool]=None