from typing_extensions import Literal, Dict
from states import State



def input_decide_edge(state: State) -> Literal["vision_node", "injection_node"]:        
        if state.input_type == "image":
            return "vision_node"
        elif state.input_type == "text":
            return "injection_node"
        
        
def workflow_edge(state: State) -> Literal["context_node", "scraping_node_tav", "chatbot_node"]:
        if state.product_info == None:
            return "chatbot_node"

        if state.input_type == "image":
            return "chatbot_node"
        if state.workflow== "Wiki_tool":
            return "context_node"
        elif state.workflow == "links_tool":
            return "scraping_node_tav"
        else:
            return "chatbot_node"
        

def context_decide_edge(state: State) -> Literal["wiki_node", "message_to_memory"]:
        if state.routing.is_context_enough == 'NOT FOUND':
            return "wiki_node"
        else:
            return "message_to_memory"
        
def wiki_decide_edge(state: State) -> Literal["wiki_chatbot_node", "message_to_memory"]:
        if state.routing.is_wiki_enough == 'NOT FOUND':
            return "wiki_chatbot_node"
        else:
            return "message_to_memory"