from state import State
from tools import ImageAnalyzer
from langgraph.graph import START,END,StateGraph
from langchain_core.messages import HumanMessage,AIMessage
from shopping_link_scrape import ShoppingLinkScraper
from langchain_community.tools import DuckDuckGoSearchResults

class Shopping_agent:
    def __init__(self, llm_dict: dict):
        self.llm_dict = llm_dict
        self.llm = self.llm_dict["llm"]
        self.image_analyzer = ImageAnalyzer(self.llm_dict)
        # Replace ShoppingLinkScraper with DuckDuckGoSearchResults
        self.shopping_search_tool = DuckDuckGoSearchResults()
        self.graph = self.compile_graph()
    
    def compile_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("router", self.router)
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_node("analyze_image", self.image_analyzer.analyze_image)
        graph_builder.add_node("search_products", self.search_products)
        
        graph_builder.add_conditional_edges(
            "router", 
            self.should_continue, 
            ["chatbot", "analyze_image", "search_products", END]
        )
        
        graph_builder.add_edge(START, "router")
        graph_builder.add_edge("analyze_image", "router")  
        graph_builder.add_edge("chatbot", "router")
        graph_builder.add_edge("search_products", "chatbot")
        
        return graph_builder.compile()
    
    async def chatbot(self, state: State) -> State:
        if "messages" not in state:
            state["messages"] = []
        elif not isinstance(state["messages"], list):
            state["messages"] = [state["messages"]]
        
        human_message = None
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                human_message = msg
                break
        
        # If we have product search results, include them in the response
        if state.get("product_search_results") and human_message:
            # Format product results nicely
            product_results = ""
            for i, product in enumerate(state["product_search_results"], 1):
                product_results += f"{i}. {product['title']}\n"
                # Handle price differently since DuckDuckGo results don't have a price field
                if 'price' in product:
                    price = product['price'] if isinstance(product['price'], (int, float)) else 'Price not available'
                    product_results += f"   Price: ${price}\n"
                product_results += f"   URL: {product['link'] if 'link' in product else product.get('url', 'No URL available')}\n"
                if 'snippet' in product:
                    product_results += f"   Description: {product['snippet']}\n"
                product_results += "\n"
            
            prompt = f"""
            Based on the following product search results:
            {product_results}
            
            Please answer this user query:
            {human_message.content}
            
            Include information about the products and make recommendations based on the query.
            If price information is available, mention it. Otherwise, just focus on the product details.
            """
            
            response = await self.llm.ainvoke(prompt)
            response_text = response
            if isinstance(response, str):
                response_text += "\n\n[product_search_results_delivered]"
                ai_message = AIMessage(content=response_text)
                state["messages"].append(ai_message)
            else:
                # If response is already an AIMessage object
                response.content += "\n\n[product_search_results_delivered]"
                state["messages"].append(response)
            
            # Clear product results after using them, so we don't show them again
            state["product_search_results"] = None
            
        # If we have image analysis results, include them in the response
        elif state.get("analysis_result") and human_message:
            prompt = f"""
            Based on the following image analysis:
            {state['analysis_result']}
            
            Please answer this user query:
            {human_message.content}
            """
            
            response = await self.llm.ainvoke(prompt)
            if isinstance(response, str):
                ai_message = AIMessage(content=response)
                state["messages"].append(ai_message)
            else:
                state["messages"].append(response)
        
        # Regular chat mode
        else:
            chat_messages = state["messages"]
            response = await self.llm.ainvoke(chat_messages)
            if isinstance(response, str):
                ai_message = AIMessage(content=response)
                state["messages"].append(ai_message)
            else:
                if isinstance(response, list):
                    state["messages"].extend(response)
                else:
                    state["messages"].append(response)
        
        return state

    # Router remains the same
    async def router(self, state: State) -> State:
        """Router node that processes the state and prepares it for the next node"""
        if "messages" not in state:
            state["messages"] = []
        if state.get("product_search_intent", False):
            # Clear the flag to prevent re-routing
            state.pop("product_search_intent", None)
        return state

    # should_continue remains the same
    def should_continue(self, state: State):
        """Conditional router that determines the next node to execute"""
        messages = state.get("messages", [])
        if not messages:
            return "chatbot"
        
        last_message = messages[-1] if isinstance(messages, list) and messages else messages
        
        has_analysis = state.get("analysis_result") is not None
        image_received = state.get("image_path") is not None and not state.get("image_path_processed", False)
        
        if isinstance(last_message, AIMessage) and "product_search_results" in str(last_message.content):
            return END
            
        if state.get("product_search_intent", False):
            # Clear the flag here to prevent re-routing next time
            state.pop("product_search_intent", None)
            return "search_products"
        
        # If it's a human message, analyze its content for routing
        if isinstance(last_message, HumanMessage):
            content = last_message.content.lower() if isinstance(last_message.content, str) else ""
            
            # Check if this message has already been processed for product search
            message_id = getattr(last_message, 'id', None)
            processed_messages = state.get("processed_search_messages", set())
            
            # Check for product search intent
            search_keywords = ["search", "find", "buy", "purchase", "shop", "product", "shopping"]
            has_search_intent = any(word in content for word in search_keywords)
            
            # Check if we have an image to analyze
            if image_received:
                return "analyze_image"
            elif has_search_intent and message_id not in processed_messages:
                # Mark this message as processed for product search
                if message_id:
                    processed_messages.add(message_id)
                    state["processed_search_messages"] = processed_messages
                return "search_products"
            # Handle exit commands
            elif has_analysis and any(word in content for word in ["done", "exit", "finish", "stop"]):
                state["analysis_result"] = None
                state["image_path_processed"] = False
                return "chatbot"
            # Default to chatbot
            else:
                return "chatbot"
        
        # After completing a product search, ensure we route to chatbot
        elif state.get("product_search_results") is not None:
            return "chatbot"
        
        # End condition
        elif isinstance(last_message, AIMessage):
            return END
        
        return END
    
    # process_message remains the same
    async def process_message(self, message_content, message_type="text", image_path=None):
        """
        Entry point for incoming WhatsApp messages
        
        Args:
            message_content: The content of the message (text)
            message_type: Either "text" or "image" 
            image_path: Path to the image if message_type is "image"
        
        Returns:
            Response message to send back to user
        """
        # Initialize or get the current state for this user
        # In a real implementation, you'd maintain state per user session
        state = self.get_or_create_user_state()
        
        # Process message based on type
        if message_type == "image":
            state["image_path"] = image_path
            # Let the user know we received their image
            return "I received your image! What would you like to know about it?"
        
        # For text messages
        state["messages"].append(HumanMessage(content=message_content))
        
        # Check for product search intent
        if any(word in message_content.lower() for word in ["search", "find", "buy", "purchase", "shop", "product", "shopping"]):
            state["product_search_intent"] = True
        
        # Run the agent
        state = await self.run_agent(state)
        
        # Extract the response to send back
        if "messages" in state and state["messages"]:
            last_message = state["messages"][-1]
            if isinstance(last_message, AIMessage):
                return last_message.content
        
        # Default response if something went wrong
        return "I'm processing your request."
    
    # run_agent and get_node_function remain the same
    async def run_agent(self, state):
        """Run the agent on the current state"""
        # Get the next node to run based on the current state
        next_node = self.should_continue(state)
        
        # Run nodes until we reach END
        while next_node != END:
            # Get the function for the current node
            node_func = self.get_node_function(next_node)
            
            # Execute the node function
            state = await node_func(state)
            
            # Determine the next node
            next_node = self.should_continue(state)
        
        return state
    
    def get_node_function(self, node_name):
        """Get the function for a node by name"""
        node_map = {
            "router": self.router,
            "chatbot": self.chatbot,
            "analyze_image": self.image_analyzer.analyze_image,
            "search_products": self.search_products
        }
        return node_map.get(node_name)
    
    def get_or_create_user_state(self):
        """
        In a real implementation, this would get the state for a specific user
        or create a new one if it doesn't exist
        """
        # Simplified implementation - in production, you'd use a database or cache
        return {"messages": []}
    
    # Updated search_products method to use DuckDuckGoSearchResults
    async def search_products(self, state: State) -> State:
        """Search for products based on user query or image analysis using DuckDuckGo"""
        # Get the query from the last human message
        human_message = None
        for msg in reversed(state.get("messages", [])):
            if isinstance(msg, HumanMessage):
                human_message = msg
                break
        
        if not human_message:
            return state
        
        query = human_message.content
        
        # Enhance query with image analysis if available
        enhanced_query = query
        if state.get("analysis_result"):
            # Use LLM to create a better shopping query based on image analysis
            prompt = f"""
            Based on this image analysis:
            {state['analysis_result']}
            
            And this user query:
            {query}
            
            Create a detailed shopping search query that includes specific details
            from the image analysis that would help find similar products.
            Be specific about colors, styles, patterns, materials, brands if visible.
            Provide ONLY the search query without any additional text.
            """
            
            enhanced_query_response = await self.llm.ainvoke(prompt)
            if isinstance(enhanced_query_response, str):
                enhanced_query = enhanced_query_response
            else:
                enhanced_query = enhanced_query_response.content
        
        # Add shopping-related terms to the query to focus on shopping results
        search_query = f"{enhanced_query} shopping buy online"
        
        try:
            # Use DuckDuckGo tool to search for products
            # Format the query according to the tool's requirements
            formatted_query = {"query": search_query}
            search_results = self.shopping_search_tool.invoke(formatted_query)
            
            # Parse the results - assuming search_results is a string containing JSON data
            import json
            if isinstance(search_results, str):
                try:
                    products = json.loads(search_results)
                except json.JSONDecodeError:
                    # If not valid JSON, try to extract structured data
                    products = self._extract_search_results(search_results)
            else:
                # If already a dict or list
                products = search_results
            
            # Filter results to focus on shopping-related links
            shopping_products = self._filter_shopping_results(products)
            
            if shopping_products:
                state["product_search_results"] = shopping_products
            else:
                # Add a message to let the user know no products were found
                if "messages" not in state:
                    state["messages"] = []
                state["messages"].append(AIMessage(content="I searched for products matching your query, but couldn't find any relevant shopping results. Could you provide more details or try a different query?"))
                
        except Exception as e:
            # Handle errors
            if "messages" not in state:
                state["messages"] = []
            state["messages"].append(AIMessage(content=f"I encountered an error while searching for products: {str(e)}. Please try again."))
            
        state.pop("should_search_products", None)
        return state
    
    def _extract_search_results(self, search_results_text):
        """Extract structured data from raw search results text"""
        # Simple extraction logic - this could be improved based on the actual format
        import re
        
        results = []
        # Look for patterns like "title: ...", "link: ...", etc.
        entries = re.split(r'\n\n|\r\n\r\n', search_results_text)
        
        for entry in entries:
            if not entry.strip():
                continue
                
            result = {}
            
            # Extract title
            title_match = re.search(r'(?:title|Title)[:\s]+(.+?)(?:\n|$)', entry)
            if title_match:
                result['title'] = title_match.group(1).strip()
            
            # Extract link/URL
            link_match = re.search(r'(?:link|URL|url)[:\s]+(.+?)(?:\n|$)', entry)
            if link_match:
                result['link'] = link_match.group(1).strip()
            
            # Extract snippet/description
            snippet_match = re.search(r'(?:snippet|description|Description)[:\s]+(.+?)(?:\n|$)', entry)
            if snippet_match:
                result['snippet'] = snippet_match.group(1).strip()
            
            if result and ('title' in result or 'link' in result):
                results.append(result)
        
        return results
    
    def _filter_shopping_results(self, results):
        """Filter search results to focus on shopping-related links"""
        shopping_results = []
        
        # Shopping domains and keywords to look for
        shopping_domains = ['amazon', 'ebay', 'walmart', 'target', 'bestbuy', 'etsy', 
                           'shop', 'store', 'product', 'buy', 'purchase']
        
        if isinstance(results, list):
            for result in results:
                # Skip if no link
                if not result.get('link') and not result.get('url'):
                    continue
                    
                link = result.get('link') or result.get('url')
                title = result.get('title', '')
                
                # Check if this is a shopping result
                is_shopping = any(domain in link.lower() for domain in shopping_domains)
                if not is_shopping:
                    is_shopping = any(keyword in title.lower() for keyword in shopping_domains)
                
                if is_shopping:
                    # Add to shopping results
                    shopping_results.append(result)
                    
                    # Limit to top 5 shopping results
                    if len(shopping_results) >= 5:
                        break
        
        return shopping_results
