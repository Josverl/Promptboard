# allows to red the (python) configuration file and update the layout dictionary


def read_config(filepath: str):
    # Create a dictionary to hold the variables defined in the file
    local_vars = {}

    try:
        # Read the file content
        with open(filepath, "r") as file:
            code = file.read()

    except FileNotFoundError as e:
        print("File not found", e)
        return None

    # Execute the code in the context of the local_vars dictionary
    try:
        exec(code, {}, local_vars)
    except SyntaxError as e:
        print("Syntax error in the file", e)
        return None

    # Return the dictionary containing the variables
    return local_vars


def update_prompts(prompts: dict, filepath: str):
    if update := read_config(filepath):
        if "prompts" in update:
            prompts = update["prompts"]
        else:
            print("No prompts variable found in the file")
    return prompts
