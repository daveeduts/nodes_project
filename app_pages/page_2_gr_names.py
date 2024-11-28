import streamlit as st
from resources.utils import back_button


def page_2():
    st.title("Add Group Names")
    back_button() 

    # Properly initialize session state
    if "groups" not in st.session_state:
        st.session_state.groups = []

    # Expand or shrink `st.session_state.groups` based on `group_count`
    while len(st.session_state.groups) < st.session_state.group_count:
        st.session_state.groups.append("")
    while len(st.session_state.groups) > st.session_state.group_count:
        st.session_state.groups.pop()

    # Use a form to encapsulate inputs and the button
    with st.form("group_form"):
        # Dynamically create inputs for group names
        for i in range(st.session_state.group_count):
            st.session_state.groups[i] = st.text_input(
                f"Enter the name of group {i + 1}:",
                value=st.session_state.groups[i],
                key=f"group_{i}",
            )

        # Form submission button
        submitted = st.form_submit_button("Next")
        if submitted:
            # Perform validation
            if any(not name.strip() for name in st.session_state.groups):
                st.warning("Please enter all group names before proceeding.")
            elif len(st.session_state.groups) != len(set(st.session_state.groups)):
                st.warning("Group names must be unique.")
            elif st.session_state.main_character.strip() in st.session_state.groups:
                st.warning("Group names cannot match the main character's name.")
            else:
                # Navigate to the next page
                st.session_state.page = 3
                st.rerun()
