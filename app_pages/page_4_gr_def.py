import streamlit as st

def page_4():
    st.title("Assign Groups to Friends")

    # Ensure groups and friends are initialized
    if "groups" not in st.session_state or "friends" not in st.session_state:
        st.error("Please define groups and friends first.")
        return

    # Use a form for assigning groups
    with st.form("group_assignment_form"):
        for i, (friend_name, _) in enumerate(st.session_state.friends):
            st.write(f"Assign a group to {friend_name}:")
            options = ["No Group"] + st.session_state.groups
            selected_group = st.radio(
                label=f"Group for {friend_name}",
                options=options,
                index=options.index(st.session_state.friends[i][1][0]) if st.session_state.friends[i][1] else 0,
                key=f"group_assignment_{i}",
            )
            st.session_state.friends[i] = (
                friend_name,
                [selected_group] if selected_group != "No Group" else [],
            )

        # Submit button
        submitted = st.form_submit_button("Finish Group Assignment")
        if submitted:
            # Navigate to the next page (or complete the flow)
            st.session_state.page = 5  # Change to the next page number
            st.rerun()
