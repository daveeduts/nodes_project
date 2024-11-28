import streamlit as st

def back_button():
    if "page" in st.session_state and st.session_state.page > 1:
        if st.button("Back"):
            st.session_state.page -= 1
            st.rerun()