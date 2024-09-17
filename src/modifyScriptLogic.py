import json
import re

# File paths
input_file_path = "/home/gaurav/Desktop/SampleConversion/src/cancelAnEntireOrder2.json"
output_file_path = "/home/gaurav/Desktop/SampleConversion/src/modified_cancelAnEntireOrder2.json"


# Function to convert to camel case
def to_camel_case(s):
    components = s.split('_')
    if len(components) > 1:
        return components[0].lower() + ''.join(x.capitalize() for x in components[1:])
    return components[0].lower()


def process_key(key):
    parts = key.split('_')
    last_word = parts[-1]

    camel_case_last_word = ""
    for i, char in enumerate(last_word):
        if char.islower():
            if i > 0 and last_word[i - 1].isupper() and i == 1:
                camel_case_last_word = last_word[0].lower() + last_word[1:]
            else:
                camel_case_last_word = last_word[:i - 1].lower() + last_word[i - 1:]
            break

    # Create the new key
    original_key_no_underscores = ''.join(parts[:-1]) + last_word
    new_key = f"{camel_case_last_word}__{original_key_no_underscores}"

    return new_key


# Read the input JSON file
with open(input_file_path, 'r') as infile:
    data = json.load(infile)

# Create a new dictionary for the modified JSON
modified_data = {
    "scenario": {
        "id": data["feature"].get("id"),
        "description": data["feature"].get("description"),
        "params": data["feature"].get("params", []),
        "timestamp": data["feature"].get("timestamp"),
        "steps": {}
    }
}

# Modify "scenarios" to "steps" and process the fields
for scenario_key, scenario_value in data["feature"]["scenarios"].items():
    # Remove specific fields
    for field in ['uservice', 'compareMode', 'dependsOnPrevious', 'headerParams']:
        if field in scenario_value:
            del scenario_value[field]

    # Check if 'basePath' contains '$'
    base_path_has_dollar = 'basePath' in scenario_value and '$' in scenario_value['basePath']

    # Process queryParams if present and check for '$'
    if 'queryParams' in scenario_value:
        scenario_value['queryParams'] = [
            qp for qp in scenario_value['queryParams']
            if '$' in qp.get('value', '')
        ]
        query_params_has_dollar = any('$' in qp.get('value', '') for qp in scenario_value['queryParams'])

        # Remove queryParams if it has no elements left
        if not scenario_value['queryParams']:
            del scenario_value['queryParams']
    else:
        query_params_has_dollar = False

    # Skip the scenario if neither basePath nor queryParams contain '$'
    if not base_path_has_dollar and not query_params_has_dollar:
        continue

    # Rename 'params' to 'paramsToSave' inside the scenario
    if 'params' in scenario_value:
        scenario_value['paramsToSave'] = scenario_value.pop('params')

    # Generate the new key for the scenario
    new_key = process_key(scenario_key)

    # Add the modified scenario to the "steps" field
    modified_data["scenario"]["steps"][new_key] = scenario_value

# Write the modified content to a new JSON file
with open(output_file_path, 'w') as outfile:
    json.dump(modified_data, outfile, indent=4)

print(f"Modified file created at: {output_file_path}")
