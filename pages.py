import streamlit as st
from itertools import combinations
from pyvis.network import Network

# Helper function to set the next page
def go_to_page(page_number):
    st.session_state.page = page_number

# Page 1: Main Character and Initial Info
def page_1():
    st.title("Main Character and Initial Info")

    st.session_state.main_character = st.text_input("Enter your name:", "")
    st.session_state.group_count = st.number_input("How many groups do you want to add?", min_value=0, step=1)
    st.session_state.friend_count = st.number_input("How many friends do you want to add?", min_value=1, step=1)

    st.button("Next", on_click=go_to_page, args=(2 if st.session_state.group_count > 0 else 3,))


# Page 2: Add Group Names
def page_2():
    st.title("Add Group Names")
    
    groups = []
    for i in range(st.session_state.group_count):
        group_name = st.text_input(f"Enter the name of group {i + 1}:", key=f"group_{i}")
        groups.append(group_name.strip())

    if st.button("Next"):
        if any(not name for name in groups):
            st.warning("Please enter all group names before proceeding.")
        elif len(groups) != len(set(groups)):
            st.warning("Group names must be unique.")
        elif st.session_state.main_character.strip() in groups:
            st.warning("Group names cannot match the main character's name.")
        else:
            st.session_state.groups = groups
            go_to_page(3)  # Move to the next page


# Page 3: Add Friends and Assign Groups
def page_3():
    st.title("Add Friends" + (" and Assign Groups" if st.session_state.group_count > 0 else ""))
    
    friends = []
    all_friends_entered = True
    friend_names = []

    for i in range(st.session_state.friend_count):
        friend_name = st.text_input(f"Enter the name of friend {i + 1}:", key=f"friend_{i}").strip()
        friend_names.append(friend_name)

        if not friend_name:
            all_friends_entered = False

        if st.session_state.group_count > 0:
            st.write(f"Select a group for {friend_name}:")
            options = ["No Group"] + st.session_state.groups
            selected_group = st.radio(label=f"Select a group:", options=options, key=f"group_radio_{i}")
            selected_group = None if selected_group == "No Group" else selected_group
        else:
            selected_group = None

        friends.append((friend_name, [selected_group] if selected_group else []))

    if st.button("Next"):
        if not all_friends_entered:
            st.warning("Please enter all friend names.")
        elif len(friend_names) != len(set(friend_names)):
            st.warning("Friend names must be unique.")
        elif st.session_state.main_character.strip() in friend_names:
            st.warning("Friend names cannot match the main character's name.")
        elif any(friend in st.session_state.groups for friend in friend_names):
            st.warning("Friend names cannot match group names.")
        else:
            st.session_state.friends = friends
            go_to_page(4)  # Move to the next page


# Page 4: Define Friendships
def page_4():
    st.title("Define Friendships")

    links = {}
    processed_pairs = set()

    for idx, person_a in enumerate(st.session_state.friends):
        name_a, _ = person_a
        options = [
            friend[0]
            for friend in st.session_state.friends
            if friend[0] != name_a and (name_a, friend[0]) not in processed_pairs
        ]
        
        selected_connections = []
        if options:
            st.write(f"Who does {name_a} know?")
            cols = st.columns(3)
            for idx, option in enumerate(options):
                col = cols[idx % 3]
                with col:
                    if st.checkbox(option, key=f"{name_a}_{option}"):
                        selected_connections.append(option)
                processed_pairs.add((name_a, option))
                processed_pairs.add((option, name_a))

        for option in selected_connections:
            links[tuple(sorted((name_a, option)))] = 1

    remaining_pairs = [
        (name_a, name_b)
        for name_a, name_b in combinations([f[0] for f in st.session_state.friends], 2)
        if (name_a, name_b) not in processed_pairs and (name_b, name_a) not in processed_pairs
    ]

    if remaining_pairs:
        for name_a, name_b in remaining_pairs:
            st.write(f"Does {name_a} know {name_b}?")
            choice = st.radio(
                label=f"Select Yes or No for {name_a} and {name_b}",
                options=["Yes", "No"],
                key=f"radio_{name_a}_{name_b}",
            )

        if st.button("Next"):
            for name_a, name_b in remaining_pairs:
                choice = st.session_state.get(f"radio_{name_a}_{name_b}")
                links[tuple(sorted((name_a, name_b)))] = 1 if choice == "Yes" else 0

            st.session_state.links = links
            go_to_page(5)  # Move to the next page
    else:
        st.button("Finish", on_click=go_to_page, args=(5,))

def page_5():
    st.title(f"{st.session_state.main_character}'s Friendships")

    ego = st.session_state.main_character
    friends = st.session_state.friends
    links = st.session_state.links
    groups = st.session_state.groups

    # Placeholder for the graph
    graph_placeholder = st.empty()

    # Collect settings in an expander under the graph
    with st.expander("Show/Hide Customizations"):
        st.header("Visualization Settings")

        # Main character node color
        ego_color = st.color_picker("Choose Main Character Node Color", "#FF0000")
        
        # Handle group colors or a single color for all nodes
        group_colors = {}
        if groups:
            st.subheader("Group Colors")
            for group in groups:
                group_colors[group] = st.color_picker(f"Color for Group: {group}", "#00FF00")
        else:
            all_nodes_color = st.color_picker("Choose Color for All Nodes", "#00FF00")
        
        # Node size and physics
        node_size = st.slider("Node Size", 10, 100, 25)
        enable_physics = st.checkbox("Enable Physics", value=True)

        # Font customization
        st.header("Font Customization")
        font_color = st.color_picker("Font Color", "#000000")
        font_size = st.slider("Font Size", 10, 40, 14)
        font_face = st.selectbox("Font Face", ["arial", "verdana", "tahoma", "times new roman"])

    # Generate the graph and display it in the placeholder
    with graph_placeholder:
        # Initialize the network
        nt = Network(height="600px", width="100%", notebook=False, directed=False)

        # Apply physics settings
        if not enable_physics:
            nt.set_options("""
            var options = {
                "physics": {
                    "enabled": false
                }
            }
            """)

        # Add the main character node
        nt.add_node(
            ego,
            label=ego,
            color=ego_color,
            size=node_size + 10,
            font={"color": font_color, "size": font_size, "face": font_face}
        )

        # Add friend nodes and edges
        for name, assigned_groups in friends:
            # Determine color based on group or use a default color
            if groups:
                group_text = ", ".join(assigned_groups) if assigned_groups else "No Group"
                node_color = group_colors[assigned_groups[0]] if assigned_groups else "#CCCCCC"
            else:
                group_text = "No Groups"
                node_color = all_nodes_color

            nt.add_node(
                name,
                label=name,
                color=node_color,
                size=node_size,
                title=group_text,
                font={"color": font_color, "size": font_size, "face": font_face}
            )
            nt.add_edge(ego, name)

        # Add edges for links between friends
        for (p1, p2), value in links.items():
            if value == 1:
                nt.add_edge(p1, p2)

        # Generate the HTML and display the network
        html = nt.generate_html(notebook=False)
        st.components.v1.html(html, height=600, scrolling=False)
