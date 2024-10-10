import os
import shutil


# Function to move JSON files
def transfer_json_files(source_folder, destination_folder):
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Loop through all files in the source folder
    for file_name in os.listdir(source_folder):
        # Check if the file is a JSON file
        if file_name.endswith('.json'):
            source_path = os.path.join(source_folder, file_name)
            destination_path = os.path.join(destination_folder, file_name)

            # Move the JSON file to the destination folder
            shutil.move(source_path, destination_path)
            print(f"Transferred {file_name} to {destination_folder}")


# # Example usage
# source_folder = r"D:\NER-TRANSFERMER\dataset\vessel_info\123"
# destination_folder = r"D:\NER-TRANSFERMER\dataset\vessel_info\train"
#
# # Call the function to transfer the JSON files
# transfer_json_files(source_folder, destination_folder)


from datetime import datetime
current_year = datetime.now().year
print(current_year)