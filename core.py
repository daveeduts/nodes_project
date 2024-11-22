from itertools import combinations
from pyvis.network import Network
import networkx as nx

def people_names():
    
    inv_pers = []
    
    while True:
        n_pers = input("How many friends do you want to add? \n")
        if  not n_pers.isdigit():
            print("Please enter a valid number!")
            continue
        if int(n_pers) < 3:
            print("You should have at least three friends :D!")
            continue
        break
        
    for person in range(int(n_pers)):
        person_name = input(f"What is his name? (Person {person + 1}/{max(range(int(n_pers))) + 1}): ")
        inv_pers.append(person_name)

    return inv_pers


def group_names():
    
    inv_groups = []
    n_atr = input("How many groups do you want to add? (eg. family, friends, collegues, work) \n")
    
    if int(n_atr) >= 0:
        for group in range(int(n_atr)):
            group_name = input(f"What is the group's name? (Group {group + 1} / {max(range(int(n_atr)))+ 1}): ")
            inv_groups.append(group_name)
        
    return inv_groups

def people_info():

    inv_attribute = []
    
    people = people_names()
    groups = group_names()

    for person in people:
        
        if len(groups) > 0:
            while True:
                group_name = input(f"What group do you want to assign {person} to?: ")
                
                if group_name in groups:
                    inv_attribute.append(group_name)
                    break
                else: 
                    print(f"This group does not exist, please use one of the groups: {groups}")
        else:
            inv_attribute.append("")
    
    return list(zip(people, inv_attribute))

def links(p_info):
    inv_links = {}

    # Use combinations to generate unique pairs
    for person_a, person_b in combinations(p_info, 2):
        name_a, _ = person_a
        name_b, _ = person_b

        while True:
            link = input(f"Does {name_a} know {name_b}? (y/n): ").strip().lower()
            if link == 'y':
                inv_links[tuple(sorted((name_a, name_b)))] = 1
                break
            elif link == 'n':
                inv_links[tuple(sorted((name_a, name_b)))] = 0
                break
            else:
                print("Wrong answer! Use 'y' or 'n' ")
                continue
    return inv_links

def graph_builder():
    
    nt = Network()
    node_info = people_info()
    link_info = links(node_info)

    for name, group in node_info:
        nt.add_node(name, title=f'Group: {group}')

    for (p1, p2), value in link_info.items():
        if value == 1:
            nt.add_edge(p1, p2)
    
    nt.show("network.html", notebook=False)

graph_builder()