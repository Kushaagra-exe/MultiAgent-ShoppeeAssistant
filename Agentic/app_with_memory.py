import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from typing_extensions import Literal, Dict
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import base64
import json
import redis
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from prompts import (
    prompt_description, prompt_info, system_prompt_context, 
    WIKI_CHATBOT_SYSTEM_PROMPT, CHATBOT_SYSTEM_PROMPT, CHATBOT_SYSTEM_DETECTION_PROMPT
)
from langchain_community.tools.tavily_search import TavilySearchResults
from helper import get_router_chain, get_llm, get_llm_client
from states import VlmResponse, State, Wiki_routing
import traceback
from datetime import datetime
# from Utils.config import REDIS_HOST,REDIS_PORT
from edges import input_decide_edge, workflow_edge, context_decide_edge, wiki_decide_edge
REDIS_CLIENT = 'redis://127.0.0.1:6379'
REDIS_HOST = '127.0.0.1'
REDIS_PORT= 6379
load_dotenv()
# tavily_api=os.environ['tavily_api']
API = os.environ['GROQ_API']
# os.environ["TAVILY_API_KEY"] = tavily_api
class RedisClient:
    _instance = None

    @classmethod
    def get_client(cls):
        if cls._instance is None:
            cls._instance = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        return cls._instance


class Shoppingass:  
    
    def handle_image(self, params: Dict) -> Dict:
        image_data_url = f"data:image/jpeg;base64,{params['content']}"
        # print(image_data_url)
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
        client = get_llm_client()
        # print(prompt_template_vision)
        
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
    
        # print("Vision resp =",response)
        try:
            return {"result": json.loads(response)}
        except json.JSONDecodeError:
            print("NON JSON RESP")
            print("response", response)
            # return response
            return {"result":response}
        
    
    
    def vision_node(self, state: State) -> State:
        print("Entered vision node")
        # print("img bytes2:",state.image_bytes[:30])
        
        prod_info = self.handle_image({'content':state.image_bytes, 'prompt': prompt_info})
        print("##########################got product info#########################")
        print(prod_info)
        prod_desc = self.handle_image({'content':state.image_bytes, 'prompt': prompt_description})
        print("##########################got product desc#########################")
        print(prod_desc)
        resp = VlmResponse(description=prod_desc['result'], product_details=prod_info['result'])
        state.product_info = resp
        print("end vision")
        # print(state)
        return state
    
    def injection_node(self,state:State):
        print("Entered injection")
        session_id=state.session_id
        #Checks redis first
        redis_key=f"user_memory:{session_id}"
        memory_json= self.redis_client.get(redis_key)
        existing_message=state.msg
        if memory_json:
            try:
                mem=json.loads(memory_json)
                if mem['product_info'] or mem['product_details']:
                    description_dict = json.loads(mem['product_info'][-1])
                    product_details_dict = json.loads(mem['product_details'][-1])
                    product_info=VlmResponse(description=description_dict,
                                            product_details=product_details_dict)
                    # print("Product info:",product_info)
                    state.product_info=product_info
                if "short_term_memory" in list(mem.keys()):
                    existing_message= mem["short_term_memory"] + existing_message
                    state.msg=existing_message
                # print("\n-------------------------------\nstate after inject: ",state)
                # print("-------------------------")     
                return state
            except Exception as e:
                print(f"short_term_memory:{e}")
            # except json.JSONDecodeError as e:
            #     return {"short_term_memory":[]}
                return state
        else:
            print(f"No Redis cache found.")
            return state


    def router_node(self, state: State) -> State:
        print("entered router")
        # print("\n-------------------------------\nstate in router: ",state)
        # print("-------------------------")    
        try:
            chain = get_router_chain()
            state.workflow = chain.invoke({'messages': state.msg[-1:]}).tool_usage
            return state
        except Exception as e:
                raise(e)


    def context_node(self, state: State) -> State:
        print("entered contextnode")
        print("\n-------------------------------\nstate in context: ",state)
        print("-------------------------")
        llm = get_llm()
        if state.product_info==None:
            print("Image not uploaded")
            return state
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
        response = response.content.strip()
        response = response.strip('\n')
        response = response.strip()

        print("Context Node - :", response)
        state.wiki_response = response
        wr = Wiki_routing(is_context_enough=response)
        state.routing = wr
        

        return state

    def wiki_node(self, state: State) -> State:
        print("entered contextnode")

        if state.product_info==None:
            print("Image not uploaded")
            return state
        wiki_wrappper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=2000)
        wiki_tool = WikipediaQueryRun(api_wrapper= wiki_wrappper)
        query = f"{state.product_info.product_details['product']}" 

        res = wiki_tool.invoke(query)
        print("WikiNODE - :", res)
        res = "**Wikipedia Information**: " + res
        state.wiki_data = res
        wr = Wiki_routing(is_context_enough=state.routing.is_context_enough, is_wiki_enough='NOT FOUND')
        state.routing = wr
        return state
    
    
    def wiki_chatbot_node(self, state: State) -> State:
    
        llm = get_llm()
        if state.product_info==None:
            print("Image not uploaded")
            return state
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
        # hist = state.msg + [response.content]
        # print(hist)
        # state.msg = hist
        # print(response.content)
        state.wiki_response = response.content
        state.wiki_data = response.content
        return state

    def chatbot_node(self, state: State) -> State:
        print("Entered Chatbot")
        llm = get_llm()
        user_prompt = (                
                f"### QUESTION ###\n{state.msg[-1:]}\n\n"
                
            )
        messages = None
        if state.input_type == 'image':
            messages = [
                {"role": "system", "content": CHATBOT_SYSTEM_DETECTION_PROMPT},
                {"role": "user", "content": str(state.product_info.product_details)}
            ]
        else:
            messages = [
                {"role": "system", "content": CHATBOT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]

        
        response = llm.invoke(messages)
        print("Chatbot:",response.content)
        # add this response to message history and return the state - done
        hist = state.msg + [response.content]
        state.msg = hist
        
        return state
    
    def scraping_node_tav(self, state: State) -> State:
        print("Entered scraping")

        tav_tool = TavilySearchResults(max_results=10)

        query = f"{state.product_info.product_details['product']} amazon flipkart" 
        res = tav_tool.invoke(query)
        state.links = res
        linksadd = state.msg + [res]
        state.msg = linksadd
        print("-----------res-----------------")
        print(res)
        print("----------------------------")
        return state

    def message_to_memory(self,state:State):
        try:
            newmessage = None
            if state.wiki_data is not None:
                newmessage = state.msg + [state.wiki_data]
                state.msg = newmessage
            # print("1------------",state.msg)
            if state.wiki_response is not None:
                newmessage = state.msg + [state.wiki_response]
                state.msg = newmessage
            # print("2------------",state.msg)
            
            
        except Exception as e:
            print(f"memory lol, {e}")

        try:
            print("Entered message to memory node")
            session_id=state.session_id
            msg=state.msg
            redis_key=f"user_memory:{session_id}"
            last_msg_key=f"last_message:{session_id}"
            #Retrieve existing short term memory from Redis

            existing_memory_json=self.redis_client.get(redis_key)
            input_type=state.input_type
            product_info=state.product_info
            existing_memory={}
            if input_type=="image":

                try:
                    # existing_memory=json.loads(existing_memory_json) if existing_memory else {"product_info":[],"product_details":[]}
                    if existing_memory_json:
                        existing_memory=json.loads(existing_memory_json)
                        ls = list(existing_memory.keys())
                        if "short_term_memory" not in ls:
                            if "product_info" not in ls:
                                existing_memory = {"product_info":[],"product_details":[], "short_term_memory": []}
                            else:
                                existing_memory = {
                                    "product_info": existing_memory["product_info"],
                                "product_details":existing_memory["product_details"],
                                "short_term_memory": []
                                }
                        else:
                            if "product_info" not in ls:
                                existing_memory = {
                                    "product_info": [],
                                "product_details":[],
                                "short_term_memory": existing_memory["short_term_memory"]
                                }
                            
                    else:
                        existing_memory = {"product_info":[],"product_details":[], "short_term_memory": []}
                except json.JSONDecodeError as e:
                    existing_memory={"product_info":[],"product_details":[]}
                description=json.dumps(product_info.description)
                product_details=json.dumps(product_info.product_details)
                existing_memory["product_info"]=existing_memory["product_info"]+[description]
                existing_memory["product_details"]=existing_memory["product_details"]+[product_details]
            else:
                try:
                    # existing_memory = json.loads(existing_memory_json) if existing_memory_json else {"short_term_memory": []}
                    if existing_memory_json:
                        existing_memory=json.loads(existing_memory_json)
                        ls = list(existing_memory.keys())
                        if "short_term_memory" not in ls:
                            if "product_info" not in ls:
                                existing_memory = {"product_info":[],"product_details":[], "short_term_memory": []}
                            else:
                                existing_memory = {
                                    "product_info": existing_memory["product_info"],
                                "product_details":existing_memory["product_details"],
                                "short_term_memory": []
                                }
                        else:
                            if "product_info" not in ls:
                                existing_memory = {
                                    "product_info": [],
                                "product_details":[],
                                "short_term_memory": existing_memory["short_term_memory"]
                                }
                            
                    else:
                        existing_memory = {"product_info":[],"product_details":[], "short_term_memory": []}
    
                except json.JSONDecodeError as e:
                    print(f"Failed to parse existing memory for user {session_id}: {str(e)}")
                    existing_memory = {"short_term_memory": []}
                existing_memory["short_term_memory"]=existing_memory["short_term_memory"]+msg
        except Exception as e:
            print(f"memory fati, {e}")

        #Process new messages
        
        now_timestamp=datetime.now().timestamp()
        try:
            with self.redis_client.pipeline() as pipe:
                pipe.setex(redis_key, 120 ,json.dumps(existing_memory))
                pipe.set(last_msg_key, now_timestamp)
                result=pipe.execute()
                # print(f"Successfully stored memory in Redis for user: {session_id}")
        except Exception as e:
            print(f"Failed to store memory in Redis for user {session_id}: {str(e)}")
        return state

    def compile_graph(self):
        graph_builder = StateGraph(State)
        
        graph_builder.add_node("vision_node", self.vision_node)
        graph_builder.add_node("injection_node", self.injection_node)
        graph_builder.add_node("router_node", self.router_node)
        graph_builder.add_node("context_node", self.context_node)
        graph_builder.add_node("wiki_node", self.wiki_node)
        graph_builder.add_node("wiki_chatbot_node", self.wiki_chatbot_node)
        graph_builder.add_node("chatbot_node", self.chatbot_node)
        graph_builder.add_node("scraping_node_tav", self.scraping_node_tav)
        graph_builder.add_node("message_to_memory", self.message_to_memory)

        
        # Add edges
        graph_builder.add_conditional_edges(START, input_decide_edge)
        graph_builder.add_edge("vision_node","router_node")
        graph_builder.add_edge("injection_node", "router_node")
        graph_builder.add_conditional_edges("router_node", workflow_edge)
        graph_builder.add_conditional_edges("context_node", context_decide_edge)
        graph_builder.add_conditional_edges("wiki_node", wiki_decide_edge)
        graph_builder.add_edge("wiki_chatbot_node", "message_to_memory")
        graph_builder.add_edge("chatbot_node", "message_to_memory")

        graph_builder.add_edge("message_to_memory", END)
        
        return graph_builder.compile()

    def __init__(self):
        self.redis_client = RedisClient.get_client()
        self.graph= self.compile_graph()
        
        

    