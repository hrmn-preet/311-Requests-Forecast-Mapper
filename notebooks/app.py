import streamlit as st

st.title('Upload and Display GIF')

# File uploader allows you to upload files
uploaded_file = st.file_uploader("Choose a GIF file", type="gif")

if uploaded_file is not None:
    # Display the GIF file
    st.image(uploaded_file, format="gif")
