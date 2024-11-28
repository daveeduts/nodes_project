import streamlit as st

def back_button():
    if "page" in st.session_state and st.session_state.page > 1:
        if st.button("Back"):
            if st.session_state.page == 3 and st.session_state.group_count == 0:
                st.session_state.page -= 2
            else:
                st.session_state.page -= 1
            st.rerun()

def home_button():
    if "page" in st.session_state:
        if st.button("Home"):
            st.session_state.page = 1
        st.rerun()