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

load_dotenv()
tavily_api=os.environ['tavily_api']
API = os.environ['GROQ_API']
# os.environ["TAVILY_API_KEY"] = tavily_api

client = Groq(api_key=API)


def clean_resp(sl):
    sl = sl.replace("\n", "").replace("  ", "")
    sl = sl.replace(',"', ', "')
    sl = sl.replace('": "', '** - ')
    sl = sl.replace(', "', '\n**')
    sl = sl.replace('{"', '**')
    sl = sl.replace('"', '')
    sl = sl.replace('[', '')
    sl = sl.replace(']', '')
    sl = sl.replace('}', '')
    sl = sl.replace(': ', '** - ')


    return sl



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
    
    menu = ["🏠 Home", "🤖 App", "📧 Contact"]
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
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("📂 Upload Image")
        uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            st.success("🛒 Image Uploaded Successfully!")
            # Display file name and size
            st.markdown(f"**Filename:** {uploaded_file.name}")
            st.markdown(f"**File Size:** {uploaded_file.size} bytes")
            
            
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
        st.header("🧠 Wiki Info")
        detection = st.checkbox("✅ Detect the Image")
        wiki = st.checkbox("✅ Get Information from Wiki")
        shopp = st.checkbox("✅ Get Shopping Links")

        

        if detection:
            if st.session_state['temp_pdf_path'] is None:
                st.warning("⚠️ Please upload an Image first.")
            else:
                try:
                    
                    with st.spinner("🔄 Processing..."):
                        image_data = uploaded_file.read()
                        image_data_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"
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
                        completion = client.chat.completions.create(
                            model="llama-3.2-90b-vision-preview",
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
                            # st.write(st.session_state.product)
                            st.write('### Detection:')
                            # st.success(response)
                            st.success(clean_resp(response))
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

    with col3:
        st.header("💬 Chatbot")
        
        if st.session_state['temp_pdf_path'] is None:
            st.info("🤖 Please upload an Image and Run detection on it")
        else:   
            # Display existing messages
            # tool = TavilySearchResults(max_results=10)
            st.write("To be done")
            

# Contact Page
elif choice == "📧 Contact":
    st.title("📬 Information")
    st.markdown("""
    ## For More Info, Reach us at 
                Kushaagra Mehta -  RA2111026030065 (UI & Gen Ai)
        Aarav Sharma -  RA2111026030078 (Gen Ai)
        Ena Tandon -  RA2111026030109 (Model Fine Tuning)
        Lakksh Bhardwaj -  RA2111026030079 (Prompt Engineering)
    """)

# Footer
st.markdown("---")
st.markdown("Developed By: Kushaagra Mehta | Aarav Sharma | Ena Tandon | Lakksh Bhardwaj")