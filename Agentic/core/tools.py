from state import State
import json 
import base64
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from typing import Optional,Dict
class ImageAnalyzer:
    def __init__(self, llm_dict: Optional[dict] = None):
        self.client = llm_dict["client"]
    
    async def analyze_image(self, state: Dict):
        """Analyze the required image asynchronously"""
        image = state.get("image_path")
        
        # Read and encode image
        with open(image, "rb") as image_file:
            image_bytes = image_file.read()
            image_data_url = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"
        
        # Prepare prompt template for vision model
        prompt_template_vision = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """What is the object in this image? Provide a brief description including its key characteristics like the brand, style, quality, and any relevant shopping information.
                        
                        Return the result in strict JSON format as follows:
                        {
                            "product": "phone",
                            "brand": "Brand Name",
                            "style": "Smartphone",
                            "quality": "High",
                            "features": ["Touchscreen", "Fast Charging", "Camera Quality"]
                        }
                        The response must be JSON with varying parameters based on the image.
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url}
                    }
                ]
            }
        ]
        
        # Call vision model API asynchronously
        # Note: Assuming the client has an async method - if not, you'll need to use
        # an executor or other async wrapper
        completion = await self.client.chat.completions.acreate(
            model="llama-3.2-90b-vision-preview",
            messages=prompt_template_vision,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        response = completion.choices[0].message.content
        
        # Validate and return the response
        if isinstance(response, dict):
            formatted_response = f"Image Analysis Result:\n\n"
            for key, value in response.items():
                if isinstance(value, list):
                    formatted_response += f"- {key}: {', '.join(value)}\n"
                else:
                    formatted_response += f"- {key}: {value}\n"
        else:
            formatted_response = f"Image Analysis Result: {response}"
        
        # Update the state with the analysis result
        state["analysis_result"] = formatted_response
        state["image_path_processed"] = True
        
        # Return the updated state
        return state