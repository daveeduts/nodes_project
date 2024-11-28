import streamlit as st
from pyvis.network import Network
from resources.utils import logo_base, home_button


    
def page_6():
    
    image_base64 = logo_base("resources/logo.png")
    st.markdown(
        f"""
        <div style="text-align: center; padding-bottom: 20px;">
            <img src="data:image/png;base64,{image_base64}" alt="Logo" style="width: 300px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f"<div class='page-5-title'>{st.session_state.main_character}'s Friendships</div>", unsafe_allow_html=True)
    
    home_button()

    ego = st.session_state.main_character
    friends = st.session_state.friends
    links = st.session_state.links
    groups = st.session_state.groups

    # Placeholder for the graph
    graph_placeholder = st.empty()

    # Collect settings in an expander under the graph
    with st.expander("Show/Hide Customizations"):
        
        enable_physics = st.checkbox("Enable Physics", value=True)
        st.markdown("<div class='page-5-header'>Visualization Settings</div>", unsafe_allow_html=True)
        # Main character node color
        ego_color = st.color_picker(f"{ego}'s color", "#FF0000")
        
        # Handle group colors or a single color for all nodes
        group_colors = {}
        if groups:
            st.markdown("<div class='page-5-header'>Group Colors</div>", unsafe_allow_html=True)
            columns = st.columns(3)  
            for idx, group in enumerate(groups):
                with columns[idx % 3]:
                    group_colors[group] = st.color_picker(f"Color for {group}", "#00FF00")

        else:
            all_nodes_color = st.color_picker("Friends color", "#00FF00")
        
        # Node size and physics
        node_size = st.slider("Node Size", 10, 100, 25)

        # Font customization
        st.markdown("<div class='page-5-header'>Font Customization</div>", unsafe_allow_html=True)
        font_color = st.color_picker("Font Color", "#000000")
        font_size = st.slider("Font Size", 10, 40, 14)
        font_face = st.selectbox("Font Face", ["arial", "verdana", "tahoma", 'roboto'])

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
