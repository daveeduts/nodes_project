import streamlit as st
from itertools import combinations
from resources.utils import back_button


def page_5():
    st.title("Define Friendships")
    back_button() 

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
            links[f'{name_a}, {option}'] = 1


    st.session_state.links = links
    st.button("Finish", on_click=st.session_state.go_to_page, args=(6,))
