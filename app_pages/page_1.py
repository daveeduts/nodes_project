import streamlit as st


def page_1():
    st.image("resources/logo.png", use_container_width=False, width=250)
    st.markdown("<div class='page-1-title'>  Build your own network!</div>", unsafe_allow_html=True)

    st.session_state.main_character = st.text_input("Enter your name:", "")
    st.session_state.group_count = st.number_input("How many groups do you want to add?", min_value=0, step=1)
    st.session_state.friend_count = st.number_input("How many friends do you want to add?", min_value=1, step=1)

    st.button("Next", on_click=st.session_state.go_to_page, args=(2 if st.session_state.group_count > 0 else 3,))
    st.markdown("<div class='page-1-footnote'> Disclaimer: Data is temporary and is NOT being collected")