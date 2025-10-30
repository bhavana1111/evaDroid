def process_file(input_file, output_file):
    clickables = []
    next_buttons = []

    # Read the input file with utf-8 encoding
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("clickables:"):
            # Extract the clickable items
            clickables_list = line.replace("clickables:[", "").replace("]", "").strip()
            clickables.append([item.strip() for item in clickables_list.split(',')])
            #print(f"Found clickables: {clickables[-1]}")  # Debug: Show the extracted clickables
        elif line.startswith("next_button:"):
            # Extract the next_button text
            next_button = line.replace("next_button:", "").strip()
            next_buttons.append(next_button)
            #print(f"Found next_button: {next_button}")  # Debug: Show the extracted next_button
        elif line.startswith("history:"):
            # Skip history lines
            continue

    # Create tuples of clickables and next_buttons
    result = [(cb, nb) for cb, nb in zip(clickables, next_buttons)]
    print(f"Final result: {result}")  # Debug: Show the final result

    # Write the output to the new file with utf-8 encoding
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(result))

# Example usage
input_file = r"C:\Users\bhava\new_files\new_files\travel\viator\viator_random.txt"  # Replace with your input file name
output_file = 'output.txt'  # Replace with your desired output file name
process_file(input_file, output_file)


'''def read_file_to_array():
    input_file='output.txt'
    # Initialize an empty list to store the lines
    content_array = []

    # Read the input file with utf-8 encoding
    with open(input_file, 'r', encoding='utf-8') as file:
        # Read each line and strip whitespace
        for line in file:
            content_array.append(line.strip())  # Add each line to the array

    return content_array'''