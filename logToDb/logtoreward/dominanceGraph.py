import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import ast

reward_dict={}
# Function to read data from an external file
def read_data_from_file(filename):
    with open(filename, 'r',encoding='utf-8') as file:
        data = file.read()
    return ast.literal_eval(data)

# Read data from the file
data = read_data_from_file(r'C:\Users\bhava\new_files\new_files\output.txt')  # Replace with your actual file path

# Initialize a dictionary to track dominance relations
click_count = defaultdict(lambda: defaultdict(int))

# Step 1: Process the data and count clicks for each pair of buttons
last_clicked_button = 'ENTRY_NODE'
for entry in data:
    # Ensure the entry has exactly two elements
    if len(entry) != 2:
        print(f"Skipping malformed entry: {entry}")
        continue  # Skip malformed entries

    available_buttons, clicked_button = entry  # Unpacking

    # Iterate over available buttons and track the click dominance
    for btn in available_buttons:
        if last_clicked_button != None and btn != last_clicked_button:
            click_count[last_clicked_button][btn] += 1  # clicked_button dominates btn
    last_clicked_button = clicked_button

# Debug: Print the click_count structure to ensure it's correct
print("Click count structure:")
for key, value in click_count.items():
    print(f"{key}: {dict(value)}")

# Step 2: Create the directed dominance graph
G = nx.DiGraph()

# Add edges to a temporary list to avoid modifying the dictionary during iteration
edges_to_add = []

# Gather dominance relationships
for btn1 in click_count:
    for btn2 in click_count[btn1]:  # btn2 iterates over the keys of the inner dictionary
        if click_count[btn1][btn2] > 0:  # Check if btn1 has clicks over btn2
            edges_to_add.append((btn1, btn2))

# Now add the edges to the graph
G.add_edges_from(edges_to_add)

# Step 3: Calculate rewards for only next buttons
# Collect all clicked buttons while ensuring the data format is correct
next_buttons = set()
for entry in data:
    if len(entry) == 2:  # Ensure the entry has two elements
        _, clicked_button = entry
        next_buttons.add(clicked_button)

# Calculate rewards for the next buttons

ancesters = dict() # dictionary from each node to the set of ancesters
dominators = dict() # dictionary from each node to the set of dominators
rewards = dict() # dictionary from each node to its reward
allnodes = set(list(G.nodes()))

for node in G:
    rewards[node] = 1
    dominators[node] = set()
    dominators[node].add(node)
    ancesters[node] = set()

changed = True
while changed:
    changed = False
    for node in G:
        oridom = len(dominators[node])
        orianc = len(ancesters[node])
        doms = allnodes
        for pre in G.predecessors(node):
            ancesters[node] = ancesters[node] | ancesters[pre]
            doms = doms & dominators[pre]
        if len(doms) > 0:
            dominators[node] = dominators[node] | doms
        if len(dominators[node]) > oridom or len(ancesters[node]) > orianc:
            changed = True
   
for node in G:
    for dom in dominators[node]:
        rewards[node] = rewards[node] + 1

'''
for node in next_buttons:
    if node in G:  # Ensure the node exists in the graph
        out_degree = G.out_degree(node)  # How many nodes this node dominates
        in_degree = G.in_degree(node)    # How many nodes dominate this node
        rewards[node] = out_degree - in_degree  # Reward based on out-degree minus in-degree
'''

# Print the rewards for each next button
print("Rewards for each next button:")
for node, reward in rewards.items():
    reward_dict[node]=reward

    #print(f"Button {node}: Reward = {reward}")

#deleted visualization