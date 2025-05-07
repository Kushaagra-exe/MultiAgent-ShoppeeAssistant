import streamlit as st
import base64

uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

image_data = uploaded_file.read()

image_data_url = base64.b64encode(image_data).decode()

st.write(image_data_url)
