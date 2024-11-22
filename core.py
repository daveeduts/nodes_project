from itertools import combinations
from pyvis.network import Network
import networkx as nx


# Implement central node by creating node name with no attributes and links to all nodes 


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

    for i,person in enumerate(people):

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


# Calculating links between nodes based on unique combinations of people 
def links(p_info):
    
    inv_links = {}
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


# Graph builder corpus -> To update colors and weight of links
def graph_builder():
    
    nt = Network()
    
    ego = input("What is your name?\n")
    nt.add_node(ego, title="Main Character Vibes", color="red")
    
    node_info = people_info()
    link_info = links(node_info)

    for name, group in node_info:
        nt.add_node(name, title=f'{group}')
    
    for name, _ in node_info:
        nt.add_edge(ego, name)

    for (p1, p2), value in link_info.items():
        if value == 1:
            nt.add_edge(p1, p2)
    
    nt.show("network.html", notebook=False)


def main():
    graph_builder()



if __name__ == "__main__":
    main()