import streamlit as st
from app_pages.page_1 import page_1
from app_pages.page_2_gr_names import page_2
from app_pages.page_3_fr_names import page_3
from app_pages.page_4_gr_def import page_4
from app_pages.page_5_links import page_5
from app_pages.page_6_graph import page_6


st.set_page_config(
    page_title="NETRA - Network Builder",
    page_icon="🕸️",
    layout="centered",
)

with open("resources/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def go_to_page(page_number):
    st.session_state.page = page_number

if "go_to_page" not in st.session_state:
    st.session_state.go_to_page = go_to_page

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


def main():
    if st.session_state.page == 1:
        page_1()
    elif st.session_state.page == 2:
        page_2()
    elif st.session_state.page == 3:
        page_3()
    elif st.session_state.page ==4:
        page_4()
    elif st.session_state.page == 5:
        page_5()
    elif st.session_state.page == 6:
        page_6()

if __name__ == "__main__":
    main()
