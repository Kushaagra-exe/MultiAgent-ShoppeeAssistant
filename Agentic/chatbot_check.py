import streamlit as st
import time

def xyz_function(message):
    """
    This function processes the user's message.
    You can modify this to implement your specific processing logic.
    """
    # Simulate processing time
    time.sleep(1)
    
    # Process the message (this is where your actual logic would go)
    processed_result = f"Processed: '{message}' through xyz function"
    
    return processed_result

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
</style>
""", unsafe_allow_html=True)

# App title
st.title("Function-Invoking Chatbot")
st.markdown("Type a message and the assistant will invoke the xyz function with your message.")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input


user_input = st.chat_input("Type your message here...")

# Process the user input when provided
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Invoke xyz function with user's message
    with st.spinner("Processing..."):
        result = xyz_function(user_input)
    
    # Display assistant's response with the function result
    with st.chat_message("assistant"):
        st.write(f"I've invoked the xyz function with your message. Here's the result:")
        st.code(result)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"I've invoked the xyz function with your message. Here's the result:\n\n```\n{result}\n```"
    })