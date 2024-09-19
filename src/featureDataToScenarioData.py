from config import FEATURE_FILE_NAME, FEATUREDATA_DIR_PATH, SCENARIODATA_DIR_PATH, DICTIONARY_API


import json
import re
import os

# Enter feature file name here
featureDataFileName = FEATURE_FILE_NAME+".json"

# File paths
input_file_path = os.path.join(FEATUREDATA_DIR_PATH, featureDataFileName)
output_dir_path = os.path.join(SCENARIODATA_DIR_PATH, os.path.splitext(featureDataFileName)[0])

# Ensure the output directory exists (without .json in the directory name)
os.makedirs(output_dir_path, exist_ok=True)


# Dictionary for Exceptional API name suffix in scenario names
exception_transforms = DICTIONARY_API


# Function to convert to camel case
def to_camel_case(s):
    components = s.split('_')
    if len(components) > 1:
        return components[0].lower() + ''.join(x.capitalize() for x in components[1:])
    return components[0].lower()


# Function to process keys and handle exceptions
def process_key(key):
    parts = key.split('_')
    last_word = parts[-1]

    # Check if the last word is in the exception list
    if last_word in exception_transforms:
        transformed_last_word = exception_transforms[last_word]
    else:
        # Convert last_word to camel case if it's not in the exceptions
        camel_case_last_word = ""
        for i, char in enumerate(last_word):
            if char.islower():
                if i > 0 and last_word[i - 1].isupper() and i == 1:
                    camel_case_last_word = last_word[0].lower() + last_word[1:]
                else:
                    camel_case_last_word = last_word[:i - 1].lower() + last_word[i - 1:]
                break
        else:
            camel_case_last_word = last_word.lower()

        transformed_last_word = camel_case_last_word

    # Create the new key
    original_key_no_underscores = ''.join(parts[:-1]) + last_word
    new_key = f"{transformed_last_word}__{original_key_no_underscores}"

    return new_key


# Read the input JSON file
with open(input_file_path, 'r') as infile:
    data = json.load(infile)

# Extract all unique TC types
tc_types = set()
for scenario_key in data["feature"]["scenarios"].keys():
    match = re.search(r'TC\d+', scenario_key)
    if match:
        tc_types.add(match.group())

# Create a base modified data structure
base_modified_data = {
    "scenario": {
        "id": data["feature"].get("id"),
        "description": data["feature"].get("description"),
        "params": data["feature"].get("params", []),
        "timestamp": data["feature"].get("timestamp"),
        "steps": {}
    }
}

# Create separate files for each TC type
for tc_type in tc_types:
    modified_data = base_modified_data.copy()
    modified_data["scenario"]["steps"] = {}

    for scenario_key, scenario_value in data["feature"]["scenarios"].items():
        if tc_type in scenario_key:
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
    output_file_path = os.path.join(output_dir_path, f"{FEATURE_FILE_NAME}_{tc_type}.json")
    with open(output_file_path, 'w') as outfile:
        json.dump(modified_data, outfile, indent=4)

    print(f"Modified file created at: {output_file_path}")
