import streamlit as st
from resources.utils import logo_base


def page_1():
    image_base64 = logo_base("resources/logo.png")
    st.markdown(
        f"""
        <div style="text-align: left; padding-bottom: 15px;">
            <img src="data:image/png;base64,{image_base64}" alt="Logo" style="width: 320px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div class='page-1-title'>  Build your own friendship network!</div>", unsafe_allow_html=True)

    st.session_state.main_character = st.text_input("Enter your name:", "")
    st.session_state.group_count = st.number_input("How many groups should your friends be split into?", min_value=0, step=1)
    st.session_state.friend_count = st.number_input("How many friends do you want to add?", min_value=1, step=1)

    st.button("Next", on_click=st.session_state.go_to_page, args=(2 if st.session_state.group_count > 0 else 3,))
    st.markdown("<div class='page-1-footnote'> Disclaimer: Your data is temporary and is NOT being collected!</div>", unsafe_allow_html=True)