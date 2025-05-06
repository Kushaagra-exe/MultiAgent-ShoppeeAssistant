# import streamlit as st

# def load_streamlit_updates():
#     pass

# def on_chat_submit(a,b):
#     pass

# chat_input = st.chat_input("Ask me about Streamlit updates:")
# if chat_input:
#     with st.chat_message("Bot"):
#         st.write("asda")

import streamlit as st

# Initialize chat history in session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to simulate a bot's response
def get_bot_response(user_input):
    # You can replace this with any bot logic (e.g., calling an AI model)
    return f"Bot: You said '{user_input}', how can I assist you further?"

# Function to handle sending the message
def send_message():
    user_input = st.session_state.user_input
    if user_input:
        # Add the user's message to the chat history
        st.session_state.messages.append({"role": "user", "message": user_input})
        
        # Generate bot's response and add it to the chat history
        bot_response = get_bot_response(user_input)
        st.session_state.messages.append({"role": "bot", "message": bot_response})
        
        # Clear the input field after sending the message
        st.session_state.user_input = ""

# Display the chat history using st.chat_message
def display_chat():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["message"])
        elif msg["role"] == "bot":
            st.chat_message("bot").markdown(msg["message"])

# Streamlit interface layout
st.title("Chatbot Interface with st.chat_message")

# Display the chat history
display_chat()

# User input text box
st.text_input("Your message:", key="user_input", on_change=send_message)

