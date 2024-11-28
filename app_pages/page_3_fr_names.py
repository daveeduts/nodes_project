import streamlit as st
from resources.utils import back_button


def page_3():
    st.title("Add Friends")
    back_button() 

    # Initialize `st.session_state.friends`
    if "friends" not in st.session_state:
        st.session_state.friends = []

    # Expand or shrink `st.session_state.friends` based on `friend_count`
    while len(st.session_state.friends) < st.session_state.friend_count:
        st.session_state.friends.append(("", []))
    while len(st.session_state.friends) > st.session_state.friend_count:
        st.session_state.friends.pop()

    with st.form("friend_form"):
        # Dynamically create inputs for friend names
        for i in range(st.session_state.friend_count):
            st.session_state.friends[i] = (
                st.text_input(
                    f"Enter the name of friend {i + 1}:",
                    value=st.session_state.friends[i][0],
                    key=f"friend_{i}",
                ).strip(),
                [],
            )

        # Form submission button
        submitted = st.form_submit_button("Next")
        if submitted:
            # Validation
            all_friends_entered = all(friend[0] for friend in st.session_state.friends)
            unique_names = len({friend[0] for friend in st.session_state.friends}) == len(st.session_state.friends)

            if not all_friends_entered:
                st.warning("Please enter all friend names.")
            elif not unique_names:
                st.warning("Friend names must be unique.")
            elif st.session_state.main_character.strip() in [friend[0] for friend in st.session_state.friends]:
                st.warning("Friend names cannot match the main character's name.")
            else:
                if st.session_state.group_count == 0 and st.session_state.friend_count >= 2:
                    st.session_state.page = 5# Navigate to group assignment page
                elif st.session_state.friend_count < 2:
                    st.session_state.page = 6 #Navigate to last page since there are no links
                else:
                    st.session_state.page = 4  # Change to the group assignment page number
                st.rerun()
