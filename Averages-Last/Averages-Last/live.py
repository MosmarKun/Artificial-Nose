import serial
import time
import csv
import os
import numpy as np

ser = serial.Serial("COM6", 9600)

data_name = input("Enter a data name: ")
read_frequency = float(input("Enter the reading frequency (in Hz): "))

calculated_csv_filename = "OutputDirectory/Calculated Data_1.1.csv"  # Change this to your calculated data file
csv_filename = "test.csv"  # Change this to your output data file

def format_data_name(name):
    return name[:10].ljust(10)

def predict(calculated_data, sensor_values):
    closest_data_name = None
    min_distance = float('inf')

    for calculated_name, calculated_values in calculated_data.items():
        distance = np.linalg.norm(np.array(sensor_values) - np.array(calculated_values))
        if distance < min_distance:
            min_distance = distance
            closest_data_name = calculated_name

    return closest_data_name

# Load calculated data into a dictionary
calculated_data = {}
with open(calculated_csv_filename, 'r') as calculated_csv:
    csv_reader = csv.reader(calculated_csv)
    headers = next(csv_reader)
    for row in csv_reader:
        x = row[-1]
        avg_values = list(map(float, row[:-1]))
        calculated_data[x] = avg_values

try:
    while True:
        data = ser.readline().decode('utf-8').strip()
        values = data.split(',')
        if len(values) >= 4:
            no2, c2h5ch, voc, co = map(float, values[:4])
            sensor_values = [no2, c2h5ch, voc, co]
            data_name_predicted = predict(calculated_data, sensor_values)
            print(f"Sensor Data: {sensor_values}, Predicted Class: {format_data_name(data_name_predicted)}")

            # Append data to the CSV file
            with open(csv_filename, mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([no2, c2h5ch, voc, co, data_name, data_name_predicted])

        else:
            print(f"Incomplete data: {data}")

        time.sleep(1 / read_frequency)

except KeyboardInterrupt:
    print("Serial reader terminated.")
finally:
    ser.close()
