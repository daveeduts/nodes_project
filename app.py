import streamlit as st
from itertools import combinations
from pyvis.network import Network
import tempfile
import os

# Store global data using Streamlit session state
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


# Page 1: Main Character & Counts
def page_1():
    st.title("Main Character and Initial Info")
    
    st.session_state.main_character = st.text_input("Enter your name:", "")
    st.session_state.group_count = st.number_input(
        "How many groups do you want to add?", min_value=0, step=1
    )
    st.session_state.friend_count = st.number_input(
        "How many friends do you want to add?", min_value=1, step=1
    )
    
    if st.button("Next"):
        if st.session_state.group_count > 0:
            st.session_state.page = 2  # Go to Group Names
        else:
            st.session_state.page = 3  # Skip to Friends Input


# Page 2: Group Names
def page_2():
    st.title("Add Group Names")
    
    groups = []
    all_groups_entered = True

    for i in range(st.session_state.group_count):
        group_name = st.text_input(f"Enter the name of group {i + 1}:", key=f"group_{i}")
        
        if not group_name.strip():
            all_groups_entered = False
        
        groups.append(group_name)
    
    if st.button("Next"):
        if not all_groups_entered:
            st.warning("Please enter all group names before proceeding.")
        else: 
            st.session_state.groups = groups
            st.session_state.page = 3


# Page 3: Friends and Group Assignment
def page_3():
    st.title("Add Friends" + (" and Assign Groups" if st.session_state.group_count > 0 else ""))
    
    friends = []
    all_friends_entered = True

    # Add fields for friend names and group selection
    for i in range(st.session_state.friend_count):
        friend_name = st.text_input(f"Enter the name of friend {i + 1}:", key=f"friend_{i}")
        
        # Check if name is entered
        if not friend_name.strip():
            all_friends_entered = False
        
        # Group selection (if groups exist)
        if st.session_state.group_count > 0:
                selected_group = st.radio(
                    label="Select a group:",
                    options=st.session_state.groups,
                    key=f"group_radio_{i}"
                )
        else:
            selected_group = None
            
        friends.append((friend_name, [selected_group] if selected_group else []))
    
    # Prevent proceeding if not all names are entered
    if st.button("Next"):
        if not all_friends_entered:
            st.warning("Please enter all friend names before proceeding.")
        else:
            st.session_state.friends = friends
            st.session_state.page = 4


def page_4():
    st.title("Define Friendships")

    links = {}

    # Ensure friends list is valid
    if not st.session_state.friends or any(not friend[0].strip() for friend in st.session_state.friends):
        st.warning("Please ensure all friends have valid names before proceeding.")
        return

    # Keep track of processed pairs
    processed_pairs = set()

    # Ask "Who does X know?" for each person
    for idx, person_a in enumerate(st.session_state.friends):
        name_a, _ = person_a

        # Generate options for unprocessed pairs
        options = [
            friend[0]
            for friend in st.session_state.friends
            if friend[0] != name_a and (name_a, friend[0]) not in processed_pairs
        ]

        # Render checkboxes in columns to display three per row
        selected_connections = []
        if options:
            st.write(f"Who does {name_a} know?")
            cols = st.columns(3)  # Create three columns

            for idx, option in enumerate(options):
                col = cols[idx % 3]
                with col:
                    if st.checkbox(option, key=f"{name_a}_{option}"):
                        selected_connections.append(option)
                # Mark this pair as processed
                processed_pairs.add((name_a, option))
                processed_pairs.add((option, name_a))  # Avoid reverse pair

            # Record selected connections
            for option in selected_connections:
                links[tuple(sorted((name_a, option)))] = 1

    # Handle remaining unprocessed pairs
    remaining_pairs = [
        (name_a, name_b)
        for name_a, name_b in combinations([f[0] for f in st.session_state.friends], 2)
        if (name_a, name_b) not in processed_pairs and (name_b, name_a) not in processed_pairs
    ]

    if remaining_pairs:
        st.write("Answer the following questions:")
        for name_a, name_b in remaining_pairs:
            st.write(f"Does {name_a} know {name_b}?")
            choice = st.radio(
                label=f"Select Yes or No for {name_a} and {name_b}",
                options=["Yes", "No"],
                key=f"radio_{name_a}_{name_b}"
            )

        if st.button("Next"):
            for name_a, name_b in remaining_pairs:
                choice = st.session_state.get(f"radio_{name_a}_{name_b}")
                if choice == "Yes":
                    links[tuple(sorted((name_a, name_b)))] = 1
                else:
                    links[tuple(sorted((name_a, name_b)))] = 0
                # Mark this pair as processed
                processed_pairs.add((name_a, name_b))
                processed_pairs.add((name_b, name_a))
            st.session_state.links = links
            st.session_state.page = 5
    else:
        if st.button("Finish"):
            st.session_state.links = links
            st.session_state.page = 5

# Page 5: Visualize Network
def page_5():
    st.title(f"{st.session_state.main_character}'s Friendships")

    ego = st.session_state.main_character
    friends = st.session_state.friends
    links = st.session_state.links

    nt = Network(notebook=False)
    nt.add_node(ego, title="Main Character", color="red")

    for name, groups in friends:
        if groups:  # Add group info only if groups exist
            group_text = ", ".join(groups)
            nt.add_node(name, title=f'{group_text}')
        else:
            nt.add_node(name, title="No group")
        nt.add_edge(ego, name)

    for (p1, p2), value in links.items():
        if value == 1:
            nt.add_edge(p1, p2)

    # Generate the HTML
    html = nt.generate_html(notebook=False)

    # Display the network graph in Streamlit
    st.components.v1.html(html, height=600, scrolling=False)


def main():
    if "page" not in st.session_state:
        st.session_state.page = 1
    
    if st.session_state.page == 1:
        page_1()
    elif st.session_state.page == 2:
        page_2()
    elif st.session_state.page == 3:
        page_3()
    elif st.session_state.page == 4:
        page_4()
    elif st.session_state.page == 5:
        page_5()


if __name__ == "__main__":
    main()
