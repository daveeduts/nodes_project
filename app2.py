import streamlit as st
from pages import page_1, page_2, page_3, page_4, page_5

# Load styles
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = 1
if "main_character" not in st.session_state:
    st.session_state.main_character = ""
if "group_count" not in st.session_state:
    st.session_state.group_count = 0
if "friend_count" not in st.session_state:
    st.session_state.friend_count = 0
if "groups" not in st.session_state:
    st.session_state.groups = []
if "friends" not in st.session_state:
    st.session_state.friends = []
if "links" not in st.session_state:
    st.session_state.links = {}

# Main app logic
def main():
    page_5()
    # Route to the correct page
    # if st.session_state.page == 1:
    #     page_1()
    # elif st.session_state.page == 2:
    #     page_2()
    # elif st.session_state.page == 3:
    #     page_3()
    # elif st.session_state.page == 4:
    #     page_4()
    # elif st.session_state.page == 5:
    #     page_5()

if __name__ == "__main__":
    main()
