import streamlit as st
import base64


def back_button():
    if "page" in st.session_state and st.session_state.page > 1:
        if st.button("Back"):
            if st.session_state.page == 3 and st.session_state.group_count == 0:
                st.session_state.page -= 2
            else:
                st.session_state.page -= 1
            st.rerun()


def logo_base(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    

def home_button():
    if 'page' in st.session_state:
        if st.button('🏠 Home'):
            st.session_state.page = 1
            st.rerun()

def custom_meta():
    cm = """
<head>
    <meta name="description" content="Build your own friendship network with NETRA!">
    <meta property="og:title" content="NETRA - Network Builder">
    <meta property="og:description" content="Build your own friendship network with NETRA!">
    <meta property="og:image" content="https://i.ibb.co/Xy0FM5x/app-logoo.png">
    <meta property="og:url" content="https://net-ra.streamlit.app/">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="NETRA - Network Builder">
</head>
"""
    return cm 
