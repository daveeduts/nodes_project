import streamlit as st
from itertools import combinations

def page_5():
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
            st.session_state.go_to_page(6)
    else:
        st.button("Finish", on_click=st.session_state.go_to_page, args=(6,))
