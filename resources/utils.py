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

