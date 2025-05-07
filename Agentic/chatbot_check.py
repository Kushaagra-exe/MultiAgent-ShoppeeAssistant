import streamlit as st
import time
import base64
from io import BytesIO
from PIL import Image

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
    
    if input_type == "text":
        # Process text message
        processed_result = f"Processed text: '{input_data}' through xyz function"
    else:
        # Process image (base64)
        # Here we're just acknowledging receipt of the image
        # In a real application, you might do image analysis or other processing
        image_preview = input_data[:50] + "..." if len(input_data) > 50 else input_data
        processed_result = f"Processed image (base64 preview): {image_preview}"
        st.session_state["uploaded_file"] = None
    
    return processed_result

def image_to_base64(image):
    """Convert a PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Set page configuration
st.set_page_config(page_title="Function-Invoking Chatbot", layout="wide")

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
st.title("Function-Invoking Chatbot")
st.markdown("Type a message or upload an image from the sidebar, and the assistant will invoke the xyz function.")

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
            st.image(f"data:image/jpeg;base64,{message['image']}", caption="Uploaded Image")
        else:
            # Display text message
            st.write(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

# Process the image if uploaded
if uploaded_file:
    try:
        # Open and convert the image
        image = Image.open(uploaded_file)
        
        # Convert image to base64
        img_base64 = image_to_base64(image)
        
        # Add image message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": "Uploaded an image", 
            "image": img_base64
        })
        
        # Display user's image message
        with st.chat_message("user"):
            st.image(image, caption="Uploaded Image")
        
        # Invoke xyz function with the image base64
        with st.spinner("Processing image..."):
            result = xyz_function(img_base64, input_type="image")
        
        # Display assistant's response
        with st.chat_message("assistant"):
            st.write("I've processed your image through the xyz function. Here's the result:")
            st.code(result)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"I've processed your image through the xyz function. Here's the result:\n\n```\n{result}\n```"
        })
        
        # Clear the file uploader
        st.sidebar.success("Image processed successfully!")
        
        # Force a rerun to clear the uploader
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
        st.write("I've processed your message through the xyz function. Here's the result:")
        st.code(result)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"I've processed your message through the xyz function. Here's the result:\n\n```\n{result}\n```"
    })