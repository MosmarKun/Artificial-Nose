import csv
import os
import numpy as np
from sklearn.metrics import confusion_matrix
from scipy import stats as scipy_stats  # Import scipy.stats as scipy_stats

# ... (the rest of your code remains the same)

def format_percentage(value):
    return f"{value:.2f}%".zfill(6)  # Ensure 2 digits before the decimal point and 2 digits after with zero padding

def format_matrix_value(value):
    return f"{value:.2f}%".rjust(10)  # Right-justify the value within a 10-character space

def format_data_name(name):
    return name[:10].ljust(10)  # Truncate to 10 characters and left-justify

def calculate_statistics(input_csv_path, output_dir):
    try:
        # Read the input CSV file
        with open(input_csv_path, 'r') as input_csv:
            csv_reader = csv.reader(input_csv)
            headers = next(csv_reader)
            data = {}  # Dictionary to store sensor data

            # Extract sensor values
            for row in csv_reader:
                sensor_name = row[-1]  # Last column contains the Data Name                
                sensor_values = list(map(float, row[:-1]))  # Convert values to float
                if sensor_name not in data:
                    data[sensor_name] = []
                data[sensor_name].append(sensor_values)

        threshold_values = [0.9]  # threshold value


        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        for threshold in threshold_values:
            # Calculate statistics for each sensor while excluding potential outliers
            statistics = {}
            for sensor_name, sensor_values in data.items():
                # Calculate Z-scores for each value
                z_scores = np.abs(scipy_stats.zscore(sensor_values))
                valid_indices = np.where(z_scores < threshold)
                filtered_values = [sensor_values[i] for i in valid_indices[0]]

                avg_values = np.mean(filtered_values, axis=0)
                statistics[sensor_name] = {'averages': avg_values}

            # Create an output CSV file for this threshold
            output_csv_path = os.path.join(output_dir, f'Calculated Data_{threshold}.csv')

            # Write statistics to the output CSV file
            with open(output_csv_path, 'w', newline='') as output_csv:
                csv_writer = csv.writer(output_csv)

                # Write headers
                new_headers = ['NO2', 'C2H5CH', 'VOC', 'CO', 'Data Name']
                csv_writer.writerow(new_headers)

                # Write average data
                for sensor_name, stats in statistics.items():
                    avg_row = ['%.2f' % avg for avg in stats['averages']]
                    csv_row = avg_row + [sensor_name]
                    csv_writer.writerow(csv_row)

            print(f"Statistics calculated for threshold {threshold} and saved to '{output_csv_path}'.")

            # Perform predictions and generate confusion matrix
            predict_and_evaluate("outputtesting_Air_Chocolate_Bread_Fish_Cola.csv", output_csv_path)

    except Exception as e:
        print(f"Error: {e}")

def predict_and_evaluate(test_csv_path, calculated_csv_path):
    try:
        total_samples = 0
        correct_predictions = 0
        incorrect_predictions = 0
        error_counts = {}
        total_counts = {}  # To store the total occurrences of each data name
        true_labels = []
        predicted_labels = []

        # Read the calculated data
        calculated_data = {}
        with open(calculated_csv_path, 'r') as calculated_csv:
            csv_reader = csv.reader(calculated_csv)
            headers = next(csv_reader)
            for row in csv_reader:
                data_name = row[-1]
                avg_values = list(map(float, row[:-1]))
                calculated_data[data_name] = avg_values

        # Read and predict data from testing CSV
        with open(test_csv_path, 'r') as test_csv:
            csv_reader = csv.reader(test_csv)
            headers = next(csv_reader)
            for row in csv_reader:
                total_samples += 1
                data_name = row[-1]
                sensor_values = list(map(float, row[:-1]))

                closest_data_name = None
                min_distance = float('inf')

                for calculated_name, calculated_values in calculated_data.items():
                    distance = np.linalg.norm(np.array(sensor_values) - np.array(calculated_values))
                    if distance < min_distance:
                        min_distance = distance
                        closest_data_name = calculated_name

                true_labels.append(data_name)
                predicted_labels.append(closest_data_name)

                prediction_correct = 1 if closest_data_name == data_name else 0
                if prediction_correct:
                    correct_predictions += 1
                else:
                    incorrect_predictions += 1
                    if data_name not in error_counts:
                        error_counts[data_name] = 0
                    error_counts[data_name] += 1

                if data_name not in total_counts:
                    total_counts[data_name] = 0
                total_counts[data_name] += 1

        accuracy = correct_predictions / total_samples * 100 if total_samples > 0 else 0

        print("Total samples:", total_samples)
        print("Correct predictions:", correct_predictions)
        print("Incorrect predictions:", incorrect_predictions)
        print("Accuracy: %.2f%%" % accuracy)
        print("Accuracy percentages for each data name:")
        for name, total_count in total_counts.items():
            if name in error_counts:
                error_count = error_counts[name]
                error_percentage = (total_count - error_count) / total_count * 100
                print(f"{name}: {error_percentage:.2f}%")
            else:
                print(f"{name}: 100.00%")

        # Calculate and print the confusion matrix as percentages with row and column headers
        confusion = confusion_matrix(true_labels, predicted_labels, labels=list(total_counts.keys()))
        confusion_percentage = confusion.astype('float') / confusion.sum(axis=1)[:, np.newaxis] * 100

        data_names = [format_data_name(name) for name in list(total_counts.keys())]
        print("Confusion Matrix (Percentages):")
        header_row = [""] + data_names  # Add an empty cell for alignment
        print("          ",end="")
        print(" | ".join(header_row))
        for i, row in enumerate(confusion_percentage):
            formatted_row = [format_matrix_value(value) for value in row]
            print(f"{data_names[i]} | " + " | ".join(formatted_row))

        # Save the confusion matrix to a text file
        output_txt_path = os.path.splitext(calculated_csv_path)[0] + '_ConfusionMatrix.txt'
        with open(output_txt_path, 'w') as output_txt:
            output_txt.write("Total samples: " + str(total_samples))
            output_txt.write("\tCorrect predictions: "+ str(correct_predictions))
            output_txt.write("\tIncorrect predictions: " +  str(incorrect_predictions))
            output_txt.write("\tAccuracy: %.2f%%" % accuracy)
            output_txt.write("\tConfusion Matrix (Percentages):\n")
            output_txt.write("          ")
            output_txt.write(" | ".join(header_row) + '\n')
            for i, row in enumerate(confusion_percentage):
                formatted_row = [format_matrix_value(value) for value in row]
                output_txt.write(f"{data_names[i]} | " + " | ".join(formatted_row) + '\n')

        print(f"Confusion matrix saved to '{output_txt_path}'.")

    except Exception as e:
        print(f"Error: {e}")

# Example usage
calculate_statistics('outputtraining_Air_Chocolate_Bread_Fish_Cola.csv', 'OutputDirectory_Air_Chocolate_Bread_Fish_Cola')
