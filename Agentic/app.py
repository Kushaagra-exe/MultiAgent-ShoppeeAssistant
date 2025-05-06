from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from typing_extensions import Literal, Dict
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import base64
import json
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from prompts import (
    prompt_description, prompt_info, system_prompt_context, 
    WIKI_CHATBOT_SYSTEM_PROMPT, CHATBOT_SYSTEM_PROMPT
)
from langchain_community.tools.tavily_search import TavilySearchResults
from helper import get_router_chain, get_llm, get_client
from states import VlmResponse, State
import traceback

from edges import input_decide_edge, workflow_edge, context_decide_edge, wiki_decide_edge

class Shoppingass:
    

      
    def handle_image(self, params: Dict) -> Dict:
        image_data_url = f"data:image/jpeg;base64,{base64.b64encode(params['content']).decode()}"
        prompt_template_vision = [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": params['prompt']
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": image_data_url
                                            }
                                        }
                                    ]
                                }
                            ]
        client = get_client()
        completion = client.chat.completions.create(
                                model="meta-llama/llama-4-scout-17b-16e-instruct",
                                messages=prompt_template_vision,
                                temperature=1,
                                max_tokens=1024,
                                top_p=1,
                                stream=False,
                                stop=None,
                            )
        response = completion.choices[0].message.content
        print("Vision resp =",response)
        try:
            return {"result": json.loads(response)}
        except json.JSONDecodeError:
            print("NON JSON RESP")
            return {"result":response}
    
    
    def vision_node(self, state: State) -> State:
        prod_info = self.handle_image({'content':state.image_bytes, 'prompt': prompt_info})
        prod_desc = self.handle_image({'content':state.image_bytes, 'prompt': prompt_description})
        resp = VlmResponse(description=prod_desc, product_details=prod_info)
        state.product_info = resp
        return state
    
    def injection_node():
        pass


    def router_node(self, state: State) -> State:
        try:
            chain = get_router_chain()
            state.workflow = chain.invoke({'messages': state.msg}).response_type
            return state
        except Exception as e:
                raise(e)


    def context_node(self, state: State) -> State:
        llm = get_llm()
        user_prompt = (
                f"### CONTEXT ###\n{state.product_info.description}\n\n"
                f"### QUESTION ###\n{state.msg[-1:]}\n\n"
                "Answer the question using only the context above. Also format the answer in a good short sentence"
            )

        messages = [
            {"role": "system", "content": system_prompt_context},
            {"role": "user", "content": user_prompt}
        ]

        
        response = llm.invoke(messages)
        state.wiki_response = response
        return state

    def wiki_node(self, state: State) -> State:
        wiki_wrappper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=2000)
        wiki_tool = WikipediaQueryRun(api_wrapper= wiki_wrappper)
        query = f"{state.product_info.product_details['product']}" 

        res = wiki_tool.invoke(query)
        state.wiki_data = res
        return state
    
    
    def wiki_chatbot_node(self, state: State) -> State:
    
        llm = get_llm()
        user_prompt = (
            f"### PRODUCT INFORMATION ###\n{state.product_info.description}\n\n"
            f"### GENERAL INFORMATION ###\n{state.wiki_data}\n\n"
            f"### QUESTION ###\n{state.msg[-1:]}\n\n"
        )

        messages = [
            {"role": "system", "content": WIKI_CHATBOT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        
        response = llm.invoke(messages)
        # add this response to message history and return the state

        return state

    def chatbot_node(self, state: State) -> State:

        llm = get_llm()
        user_prompt = (                
                f"### QUESTION ###\n{state.msg[-1:]}\n\n"
                
            )

        messages = [
            {"role": "system", "content": CHATBOT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        
        response = llm.invoke(messages)
        # add this response to message history and return the state
        return state
    
    def scraping_node_tav(self, state: State) -> State:             
        tav_tool = TavilySearchResults(max_results=10)

        query = f"{state.product_info.product_details['product']} amazon flipkart official website" 
        res = tav_tool.invoke(query)
        state.links = res
        return state

    def message_to_memory():
        pass
        

    def compile_graph(self):
        graph_builder = StateGraph(State)
        
        graph_builder.add_node("vision_node", self.vision_node)
        # graph_builder.add_node("injection_node", self.injection_node)
        graph_builder.add_node("router_node", self.router_node)
        graph_builder.add_node("context_node", self.context_node)
        graph_builder.add_node("wiki_node", self.wiki_node)
        graph_builder.add_node("wiki_chatbot_node", self.wiki_chatbot_node)
        graph_builder.add_node("chatbot_node", self.chatbot_node)
        graph_builder.add_node("scraping_node_tav", self.scraping_node_tav)
        # graph_builder.add_node("message_to_memory", self.message_to_memory)

        
        # Add edges
        graph_builder.add_conditional_edges(START, input_decide_edge)
        graph_builder.add_edge("vision_node","router_node")
        graph_builder.add_edge("injection_node", "router_node")
        graph_builder.add_conditional_edges("router_node", workflow_edge)
        graph_builder.add_conditional_edges("context_node", context_decide_edge)
        graph_builder.add_conditional_edges("wiki_node", wiki_decide_edge)
        # graph_builder.add_edge("wiki_chatbot_node", "message_to_memory")
        graph_builder.add_edge("wiki_chatbot_node", END)

        # graph_builder.add_edge("message_to_memory", END)

        
        

    def __init__(self):
        self.graph= self.compile_graph()