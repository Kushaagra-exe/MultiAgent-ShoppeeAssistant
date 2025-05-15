import streamlit as st
from streamlit import session_state
import time
import base64
import os
from groq import Groq
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import re
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import json
load_dotenv()
# tavily_api=os.environ['tavily_api']
API = os.environ['GROQ_API']
# os.environ["TAVILY_API_KEY"] = tavily_api
from io import BytesIO
from PIL import Image
import streamlit as st
import time
import base64
from io import BytesIO
from PIL import Image
from Agentic.app_with_memory import Shoppingass
from Agentic.states import State

client = Groq(api_key=API)
def xyz_function(input_data, input_type="text"):
    """
    This function processes either the user's message or uploaded image.
    
    Args:
        input_data: Either a text message or base64 encoded image
        input_type: "text" or "image" to indicate the type of input
    
    Returns:
        The processed result as a string
    """
    # Simulate processing time
    time.sleep(1)
    s= None
    if input_type=='image':
        # print("img bytes1:",input_data[:30])

        s = State(session_id="user1234",msg=[],input_type=input_type, image_bytes= input_data)
    
    else:
        s = State(session_id="user1234",msg=[input_data],input_type=input_type)
        
    g = Shoppingass()
    result=g.graph.invoke(s)
    result = result.get('msg')[-1]
    if input_type == "text":
        # Process text message
        processed_result = f"Processed text: '{result}'"
    else:
        # Process image (base64)
        # Here we're just acknowledging receipt of the image
        # In a real application, you might do image analysis or other processing
        image_preview = input_data
        processed_result = f"Processed image (base64 preview): {result}"
    # try:
    s=""
    if isinstance(result, list):
        for item in result:
            s += f"\n**Title:** {item['title']} \n **Url:** {item['url']} \n **Content:** {item['content']}\n"
        result = s

    print(result)
    # except Exception as e:
    #     print(f"---------------- {e}")
    return result

def image_to_base64(image, format):
    """Convert a PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format=format)

    img_str = base64.b64encode(buffered.getvalue()).decode()
    # print("type is", type(img_str))
    return img_str
    # image_data = uploaded_file.read()

    # image_data_url = base64.b64encode(image_data).decode()

def clean_resp(data):
    # sl = sl.replace("\n", "").replace("  ", "")
    # sl = sl.replace(',"', ', "')
    # sl = sl.replace('": "', '** - ')
    # sl = sl.replace(', "', '\n**')
    # sl = sl.replace('{"', '**')
    # sl = sl.replace('"', '')
    # sl = sl.replace('[', '')
    # sl = sl.replace(']', '')
    # sl = sl.replace('}', '')
    # sl = sl.replace(': ', '** - ')
    markdown = ""
    
    # Loop through the dictionary and format each key-value pair
    for key, value in data.items():
        if isinstance(value, list):  # If the value is a list (e.g., 'features')
            markdown += f"**{key.capitalize()}**:\n "
            for item in value:
                markdown += f"- {item}\n "
        else:  # If it's a single value
            markdown += f"**{key.capitalize()}**: {value}\n "
    
    return markdown



# Initialize session_state variables if not already present
if 'product' not in st.session_state:
    st.session_state['product'] = None

if 'temp_pdf_path' not in st.session_state:
    st.session_state['temp_pdf_path'] = None


st.set_page_config(
    page_title="Image Search App",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.image("logo.jpg", use_container_width =True)
    # st.markdown("### 🛒")
    st.markdown("---")
    
    menu = ["🏠 Home", "🤖 App", "🤖 Chatbot", "📧 Contact"]
    choice = st.selectbox("Navigate", menu)

if choice == "🏠 Home":
    st.title("🛒 Shoppee Assistant")
    st.markdown("""
    Welcome to **Shoppee Assistant**! 🚀

    **Built using  (LlaVa 3.2, )**

    - **Product Recognition and Detailed Insights** - Leverages advanced vision models to identify shopping items in images and generate detailed descriptions, including use cases, alternatives, and key specifications.
    - **Comprehensive Information Retrieval** - Utilizes a Wikipedia agent to fetch contextual and historical information about products, enriching user understanding and supporting informed decision-making.
    - **Online Search and Comparison** - Employs web agents to find shopping links, compare prices, and analyze product specifications across multiple e-commerce platforms, ensuring users get the best deals and options.

    
    """)

# Chatbot Page
elif choice == "🤖 App":
    st.title("🤖 Shoppee Assistant")
    st.markdown("---")
    
    col1, col2 = st.columns(2)

    with col1:
        st.header("📂 Upload Image")
        uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            st.success("🛒 Image Uploaded Successfully!")
            # Display file name and size
            # st.markdown(f"**Filename:** {uploaded_file.name}")
            # st.markdown(f"**File Size:** {uploaded_file.size} bytes")
            
            
            st.markdown("### 📖 Image Preview")
            st.image(uploaded_file)
            
            # Save the uploaded file to a temporary location
            temp_pdf_path = "temp_"+uploaded_file.name
            
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Store the temp_pdf_path in session_state
            st.session_state['temp_pdf_path'] = temp_pdf_path

    # Column 2: Create Embeddings
    with col2:
        # st.header("🧠 Wiki Info")
        detection = st.checkbox("✅ Detect the Image")
        wiki = st.checkbox("✅ Get Information from Wiki")
        shopp = st.checkbox("✅ Get Shopping Links")

        

        if detection:
            if st.session_state['temp_pdf_path'] is None:
                st.warning("⚠️ Please upload an Image first.")
            else:
                try:
                    
                    with st.spinner("🔄 Processing..."):
                        # method 1
                        # image_data = uploaded_file.read()
                        # image_data_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"

                        # method 2

                        image = Image.open(uploaded_file)
                        format = image.format

                        buffered = BytesIO()
                        image.save(buffered, format=format)
                        image_data_url = f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode()}"
                        prompt_template_vision = [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": """
What is the object in this image? Provide a brief description including its key characteristics like the brand, style, quality, and any relevant information from a shopping perspective. The result should be in JSON format where:"
"- The key product should hold the name of the object (e.g., phone), *only the product name, no brand or other descriptors*."
"- Include additional keys for other relevant details such as brand, style, quality, and any other pertinent attributes based on the image."
"- The JSON object should contain these keys in a consistent format, with the values varying based on the image content."

"Example:"
"For a picture which contains a phone, the response should look like this:
{
  "product": "phone",
  "brand": "Brand Name",
  "style": "Smartphone",
  "quality": "High",
  "features": ["Touchscreen", "Fast Charging", "Camera Quality"]
}
Select the parameters of this JSON result according to the image and there is no need to always use the given parameters
Return the result in JSON format. No description or any other content

"""
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
                        print(prompt_template_vision)
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
                        print("resp =",response)

                        match = re.search(r'"product":\s*"([^"]+)"', response)
                        try:
                            product = match.group(1)
                    
                            st.session_state.product = product
                            print("prod=", product)
                            try:
                                resp = json.loads(response)
                                st.write('### Detection:')

                                st.success(clean_resp(resp))
                            except:
                                st.write('### Detection:')
                                st.success(response)

                                
                                
                            # st.write(st.session_state.product)

                        except:
                            st.error(f"1111An error occurred\n Please Refresh the Page and try again")   

                    
                    
                except ValueError as e:
                    st.error(f"An error occurred: {e}\n Please Refresh the Page and try again")   
                    
        if wiki:
            if st.session_state['product'] is None:
                st.warning("⚠️ Please upload an Image first and Run Detection on it")
            else:
                # try:
                wiki_wrappper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500)
                wiki_tool = WikipediaQueryRun(api_wrapper= wiki_wrappper)
                with st.spinner('🔄 Processing...'):
                    query = f"what is {st.session_state.product}" 
                    res = wiki_tool.invoke(query)
                    st.write(res)
                # except:
                #     st.error(f"3333An error occurred\n Please Refresh the Page and try again")   
        if shopp:
            if st.session_state['product'] is None:
                st.warning("⚠️ Please upload an Image first and Run Detection on it")
            else:
                # try:
                tav_tool = TavilySearchResults(max_results=10)
                
                with st.spinner('🔄 Processing...'):
                    query = f"{st.session_state.product} amazon flipkart official website" 
                    res = tav_tool.invoke(query)
                    for i in range(len(res)):
                        st.write(i+1 ,res[i]['content'])
                        st.write(res[i]['url'])

elif choice == "🤖 Chatbot":
    # st.title("Chatbot")

    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .chat-container {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #e6f7ff;
        text-align: right;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .assistant-message {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .stImage img {
        max-width: 100%;
        height: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # App title in main area
    st.title("Chatbot")
    st.markdown("Type a message or upload an image from the sidebar")

    # Sidebar for image upload
    st.sidebar.title("Upload Image")
    uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("image"):
                # Display image in chat
                st.image(f"data:image/jpeg;base64,{message['image']}", caption="Uploaded Image", width=300)
            else:
                # Display text message
                st.write(message["content"])

    # Chat input
    user_input = st.chat_input("Type your message here...")

    # Process the image if uploaded
    if uploaded_file:
        try:
            # Track whether image is already processed to prevent duplicate processing
            if "last_processed_image" not in st.session_state:
                st.session_state.last_processed_image = None
                
            # Get unique identifier for the current image
            current_image_id = uploaded_file.name + str(uploaded_file.size)
            
            # Only process if this is a new image
            if st.session_state.last_processed_image != current_image_id:
                # Open and convert the image
                image = Image.open(uploaded_file)
                format = image.format

                # Convert image to base64
                img_base64 = image_to_base64(image, format)
                
                # Add image message to chat history
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Uploaded an image", 
                    "image": img_base64
                })
                
                # Display user's image message
                with st.chat_message("user"):
                    st.image(image, caption="Uploaded Image", width=300)
                
                # Invoke xyz function with the image base64
                with st.spinner("Processing image..."):
                    result = xyz_function(img_base64, input_type="image")
                
                # Display assistant's response
                with st.chat_message("assistant"):
                    # st.write("I've processed your image. Here's the result:")
                    st.write(result)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result
                })
                
                # Store this image as processed
                st.session_state.last_processed_image = current_image_id
                
                # Show success message
                st.sidebar.success("Image processed successfully!")
                
                # Force a rerun to refresh the UI
                st.rerun()
            
        except Exception as e:
            st.sidebar.error(f"Error processing image: {e}")

    # Process the user text input when provided
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Invoke xyz function with user's text message
        with st.spinner("Processing..."):
            result = xyz_function(user_input, input_type="text")
        
        # Display assistant's response
        with st.chat_message("assistant"):
            # st.write("I've processed your text. Here's the result:")
            
            st.write(result)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": result
        })
            

# Contact Page
elif choice == "📧 Contact":
    st.title("📬 Information")
    st.markdown("""
    ## For More Info, Reach us at 
    """)
    st.markdown("## Kushaagra Mehta")
    st.markdown("Linkedin - [LinkedIn](https://www.linkedin.com/in/kushaagra-mehta/)")
    st.markdown("Github - [GitHub](https://github.com/Kushaagra-exe)")
    st.markdown("Twitter - [Twitter](https://x.com/Kushaagra_exe)")
    

# Footer
st.markdown("---")
# st.markdown("Developed By: Kushaagra Mehta | Aarav Sharma | Ena Tandon | Lakksh Bhardwaj")