import json

# Function to save the list to a file
def save_to_file(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file)

# Function to load the list from a file
def load_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file does not exist
    except json.JSONDecodeError:
        print("Error decoding JSON. Returning an empty list.")
        return []