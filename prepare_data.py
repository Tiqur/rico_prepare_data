import os
import json
import shutil

# USE JSON FILES FROM SEMANTIC DATASET AND PNGS FROM UNIQUE UIS COMBINED 
# Annotation format
# https://docs.ultralytics.com/datasets/detect/

# Define the directory containing the JSON files
directory = 'combined'
labels = {}

# Create a dataset directory if it doesn't exist
output_directory = 'dataset'
os.makedirs(output_directory, exist_ok=True)

def extract_elements(data):
    """ Recursively extracts elements from the given JSON object. """
    # Initialize a list to hold the extracted elements
    elements = []

    # Check if the current data has the necessary keys
    if isinstance(data, dict):
        # Add the current element to the list
        elements.append(data)

        # If there are children, recurse into each child
        if "children" in data and isinstance(data["children"], list):
            for child in data["children"]:
                elements.extend(extract_elements(child))  # Recur for each child

    return elements

# Loop through all files in the directory
for filename in os.listdir(directory):
    # Check if the file is a JSON file
    if filename.endswith('.json'):
        # Construct the full file path
        file_path = os.path.join(directory, filename)

        # Open and load the JSON file
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)  # Load the JSON data
                file_contents = []
                image_width = data["bounds"][2]
                image_height = data["bounds"][3]

                # Images should have valid dimensions
                if image_width == 0 or image_height == 0:
                    print(file_path, "Invalid image dimensions")
                    continue

                for element in extract_elements(data):
                    if "componentLabel" in element:
                        label = element["componentLabel"]
                        bounds = element["bounds"]
                        clickable = element["clickable"]

                        # Calculate center x, center y, width, and height in pixels
                        x1, y1, x2, y2 = bounds
                        width = x2 - x1
                        height = y2 - y1
                        x_center = x1 + width / 2
                        y_center = y1 + height / 2

                        # Bounding boxes should have valid dimensions
                        if width == 0 or height == 0:
                            continue

                        # Normalize values to [0, 1]
                        normalized_x_center = x_center / image_width
                        normalized_y_center = y_center / image_height
                        normalized_width = width / image_width
                        normalized_height = height / image_height

                        if label not in labels:
                            labels[label] = len(labels)

                        # Prepare the YOLO format string
                        file_contents.append(f"{labels[label]} {normalized_x_center:.6f} {normalized_y_center:.6f} {normalized_width:.6f} {normalized_height:.6f}")

                # Determine the output base name based on the original filename
                output_base_name = os.path.splitext(filename)[0]  # Get the base name without extension

                # Copy the corresponding PNG image to the output directory
                jpg_image_path = os.path.join(directory, output_base_name + '.jpg')
                if os.path.exists(jpg_image_path):
                    shutil.copy(jpg_image_path, os.path.join(output_directory, output_base_name + '.jpg'))
                else:
                    print(f"Image not found for {filename}: {jpg_image_path}")

                # Write the annotations to the specified directory
                output_file_path = os.path.join(output_directory, output_base_name + '.txt')
                with open(output_file_path, 'w') as output_file:
                    output_file.write("\n".join(file_contents))

            except json.JSONDecodeError:
                print(f"Error decoding {filename}. Skipping.")

print("Labels:")
for k, v in labels.items():
    print(v, k)

