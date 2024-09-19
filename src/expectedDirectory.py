import os
import shutil
import re

from config import EXPECTED_DIR_PATH, FEATURE_FILE_NAME

def remove_underscores_in_filenames(directory):
    """Remove all underscores from filenames in the specified directory."""
    try:
        # List all files in the given directory
        for filename in os.listdir(directory):
            # Construct full file path
            old_file_path = os.path.join(directory, filename)

            # Check if it's a file (not a directory)
            if os.path.isfile(old_file_path) and filename.endswith(".json"):
                # Remove underscores from the filename
                new_filename = filename.replace('_', '')

                # Construct new full file path
                new_file_path = os.path.join(directory, new_filename)

                # Rename the file
                os.rename(old_file_path, new_file_path)
                print(f"Renamed: {filename} -> {new_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")


def create_unique_folders_and_move_files(base_path, target_directory):
    """Create unique folders for TC** patterns and move files into them."""
    # Dictionary to store TC** patterns and their corresponding folder paths
    tc_folders = {}

    # List all files in the target directory
    for filename in os.listdir(target_directory):
        # Find the TC** pattern in the file name using a regex
        match = re.match(r'(.*?_TC\d+)', filename)

        if match:
            tc_prefix = match.group(1)  # Get the prefix up to TC**

            # Create a folder if it doesn't exist yet
            if tc_prefix not in tc_folders:
                folder_path = os.path.join(target_directory, tc_prefix)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    print(f"Created directory: {folder_path}")

                tc_folders[tc_prefix] = folder_path

            # Move the file to the appropriate folder
            old_file_path = os.path.join(target_directory, filename)
            new_file_path = os.path.join(tc_folders[tc_prefix], filename)
            shutil.move(old_file_path, new_file_path)
            print(f"Moved file: {filename} -> {tc_folders[tc_prefix]}")

            # After moving, remove underscores from the file name inside the folder
            remove_underscores_in_filenames(tc_folders[tc_prefix])


def process_feature_file(base_path, feature_filename):
    """Process the input feature file, create scenario folders, and remove underscores from files."""

    # we find the corresponding folder
    folder_name = feature_filename

    # Construct the full path of the target directory (where the files are located)
    target_directory = os.path.join(base_path, folder_name)

    # Check if the directory exists
    if os.path.isdir(target_directory):
        print(f"Processing directory: {target_directory}")

        # Step 1: Create unique folders for each TC** and move corresponding files into them
        create_unique_folders_and_move_files(base_path, target_directory)

    else:
        print(f"Directory '{target_directory}' not found.")


# Example usage:
base_path = EXPECTED_DIR_PATH  # Define your input directory path here
feature_filename = FEATURE_FILE_NAME  # Define your feature filename here
process_feature_file(base_path, feature_filename)

