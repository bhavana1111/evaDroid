import sys
import os
from sentence_transformers import SentenceTransformer

# Append the absolute path to the directory containing dominanceGraph.py
sys.path.append(os.path.abspath('../logtoDb/logtoreward'))
from JsonToDict import reward_dict


def process_file(input_file,app_name,type):
    clickables = []
    histories = []
    next_buttons = []

    # Read the input file with utf-8 encoding
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Initialize placeholders for the fields
    current_clickables = None
    current_history = None
    current_next_button = None

    for line in lines:
        line = line.strip()

        if line.startswith("clickables:"):
            # Extract the clickable items
            clickables_list = line.replace("clickables:[", "").replace("]", "").strip()
            current_clickables = [item.strip() for item in clickables_list.split(',')]

        elif line.startswith("history:"):
            # Extract the history items
            history_list = line.replace("history:[", "").replace("]", "").strip()
            current_history = [item.strip() for item in history_list.split(',')]

        elif line.startswith("next_button:"):
            # Extract the next_button
            current_next_button = line.replace("next_button:", "").strip()

            # After reading the next_button, save the current set
            clickables.append(current_clickables or [])
            histories.append(current_history or [])
            next_buttons.append(current_next_button or "")

            # Reset the placeholders for the next set of entries
            current_clickables = None
            current_history = None
            current_next_button = None

    # Create a list of dictionaries containing clickables, histories, and next_buttons
    meta_data_list = [{"clickables": cb, "history": hb, "next_button": nb,"reward":reward_dict[nb] if nb in reward_dict else 0,"app_name":app_name,"type":type} 
              for cb, hb, nb in zip(clickables, histories, next_buttons)]
    vector = [(cb, hb) for cb, hb in zip(clickables, next_buttons)]
    print(f"Final result: {len(meta_data_list)} sets generated.")

    return meta_data_list,vector


def convertVectorToEmbedding(vector):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings=model.encode(vector)
    print(embeddings)
    similarities=model.similarity(embeddings,embeddings)
    print(similarities)
    return embeddings

def convertQueryToEmbedding(tuple):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    queryEmbeddings=model.encode(vector)
    return queryEmbeddings

# Example usageC
input_file = r"C:\Users\bhava\new_files\new_files\travel\viator\viator_random.txt"  # Replace with your input file name
app_name="Viator"
type="Random"
meta_data_list,vector=process_file(input_file,app_name,type)
embedding=convertVectorToEmbedding(vector)