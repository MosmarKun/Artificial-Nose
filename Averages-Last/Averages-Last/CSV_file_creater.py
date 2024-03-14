import cbor2
import csv
import os

def process_folder(input_folder, output_csv_path):
    # Get the folder name without the path
    folder_name = os.path.basename(input_folder)

    if folder_name == "testing":
        output_csv = "outputtesting.csv"
    elif folder_name == "training":
        output_csv = "outputtraining.csv"
    else:
        output_csv = output_csv_path

    # Create or append to the specified output CSV file
    with open(output_csv, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Iterate through all files and subfolders in the input folder
        for item in os.listdir(input_folder):
            item_path = os.path.join(input_folder, item)

            if os.path.isfile(item_path) and item.endswith(".cbor"):
                with open(item_path, 'rb') as cbor_file:
                    cbor_data = cbor2.load(cbor_file)
                    data_name = os.path.splitext(item)[0].split('.')[0]
                    values = cbor_data['payload']['values']

                    for sensor_values in values:
                        csv_row = sensor_values + [data_name]
                        csv_writer.writerow(csv_row)

            elif os.path.isdir(item_path):
                process_folder(item_path, output_csv)

def main(root_folder):
    output_csv_path = "output.csv"
    process_folder(root_folder, output_csv_path)
    print(f"Data processing complete. Output saved to '{output_csv_path}'.")

# Example usage
main(r'C:\Users\hooos\Downloads\exports')
