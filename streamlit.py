import streamlit as st
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import os
import base64
from groq import Groq
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"sample": "test"}
    ]   


st.title('Image Processing App')
client = Groq(api_key="###")

wiki_wrappper = WikipediaAPIWrapper(top_k_results=5, doc_content_chars_max=500)
wiki_tool = WikipediaQueryRun(api_wrapper= wiki_wrappper)

uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:

    st.image(uploaded_file, caption="Uploaded Image")
    image_data = uploaded_file.read()
    image_data_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"
    messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is the product in this image? Give a brief description about it in 2-3 lines in the aspect of shopping"
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
    y = st.button("Detect what it is")


    if y:
        try:
            completion = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=messages,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            response = completion.choices[0].message.content
            st.session_state.messages.append({"role": "user", "content": question, "image": image_data})
            
            st.write('### Detection:')
            st.success(response)
        except ValueError as e:
            st.error(f"An error occurred: {e}\n Please Refresh the Page")





        
        with st.spinner('Processing...'):
            query = f"what is {textbox}"  # Format the query properly
            res = wiki_tool.invoke(query)  # Querying Wikipedia
            st.write(res)

    # if y:
    #     st.write("detected: ")
    #     x= st.button("Get info")
    #     if x:
    #         st.write("Info")
        