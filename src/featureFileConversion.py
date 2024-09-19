import os
import re
from config import FEATURE_FILE_PATH, DICTIONARY_API

print(FEATURE_FILE_PATH)

# Dictionary for predefined API name conversions
api_name_mappings = DICTIONARY_API


def convert_to_custom_camel_case(s):
    """Convert string to camelCase based on the first lowercase letter and index conditions."""
    for i, char in enumerate(s):
        if char.islower():
            if i > 1:
                return s[:i - 1].lower() + s[i - 1:]
            else:
                result = []
                for j, c in enumerate(s):
                    if c.isupper() and j != 0:  # Skip the first letter since it should be lowercase
                        return ''.join(result) + s[j:]
                    result.append(c.lower())
                return ''.join(result)

    return s.lower()


def extract_wait_time_from_steps(steps):
    """Extract wait time from the steps of a scenario if present."""
    for step in steps:
        if "I will wait for" in step:
            pattern = r"I will wait for (\d+) seconds"
            match = re.search(pattern, step)
            if match:
                return f"|wait:{match.group(1)}sec"
    return ""


def extract_scenario_info(scenario_name, description, steps):
    """Extract necessary information from scenario name, description, and steps."""
    scenario_key = scenario_name.split("_")[-1]
    api_name = api_name_mappings.get(scenario_key, convert_to_custom_camel_case(scenario_key))
    data_file = scenario_name.replace("_", "")
    status_code = ""
    wait_time = extract_wait_time_from_steps(steps)

    for step in steps:
        if "The status code should be" in step:
            status_code_match = re.search(r"The status code should be (\d+)", step)
            if status_code_match:
                status_code = status_code_match.group(1)

    return f'Given "{description}(api:{api_name}|dataFile:{data_file}|statusCode:{status_code}|VR:true{wait_time})"'


def process_feature_file(input_file, output_file):
    """Reads the input feature file, processes it, and writes the transformed output."""
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()

        transformed_givens = []
        current_tag = ""
        current_scenario_name = ""
        current_description = ""
        current_steps = []
        scenario_started = False
        output_block_started = False
        feature_line = ""

        for line in lines:
            line = line.strip()

            if line.startswith("Feature:"):
                feature_line = line
                transformed_givens.append(f"{feature_line}\n")
                continue

            if line.startswith("#") or not line:
                continue

            if line.startswith("@"):
                if scenario_started:
                    transformed_givens.append(
                        extract_scenario_info(current_scenario_name, current_description, current_steps))
                    current_steps = []
                    scenario_started = False

                if current_tag != line:
                    if output_block_started:
                        transformed_givens.append("\n")
                    current_tag = line
                    output_block_started = True
                    transformed_givens.append(f"{line}")

                    if not " " in line:
                        scenario_line = line[1:].strip()
                        transformed_givens.append(f"Scenario: {scenario_line}")
                        transformed_givens.append(f"Description: ")

            elif line.startswith("Scenario:"):
                if scenario_started:
                    transformed_givens.append(
                        extract_scenario_info(current_scenario_name, current_description, current_steps))
                    current_steps = []

                current_scenario_name = line.split(":")[1].strip()
                scenario_started = True

            elif line.startswith("Description:"):
                current_description = line.split(":")[1].strip()

            elif line.startswith(("Given", "When", "Then", "And")):
                current_steps.append(line)

        if scenario_started:
            transformed_givens.append(extract_scenario_info(current_scenario_name, current_description, current_steps))

        with open(output_file, 'w') as file:
            for given_line in transformed_givens:
                file.write(f"{given_line}\n")

        print(f"Transformation complete! Output written to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Input/output file handling
def main():
    input_file = FEATURE_FILE_PATH

    # Dynamically create a "modified" directory in the current working directory
    current_directory = os.getcwd()
    modified_directory = os.path.join(current_directory, "modifiedFeatures")
    os.makedirs(modified_directory, exist_ok=True)

    # Extract file name from input_file path and append "_NEW" for the output file
    file_name = os.path.basename(input_file).split(".")[0]
    output_file = os.path.join(modified_directory, f"{file_name}_NEW.feature")

    process_feature_file(input_file, output_file)


if __name__ == "__main__":
    main()
