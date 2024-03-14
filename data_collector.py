import serial
import time
import csv
import os

ser = serial.Serial("COM6", 9600)

data_name = input("Enter a data name: ")
time_frame = float(input("Enter the time frame (in seconds): "))
read_frequency = float(input("Enter the reading frequency (in Hz): "))

csv_filename = input("Enter the CSV filename to save the data: ")

append_mode = 'a' if os.path.exists(csv_filename) else 'w'

end_time = time.time() + time_frame
i = 0

with open(csv_filename, mode=append_mode, newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    if append_mode == 'w':
        csv_writer.writerow(["NO2", "C2H5CH", "VOC", "CO", "Data Name"])

    try:
        while i != time_frame * read_frequency:
            # Read data from the serial port (you may want to add error handling)
            data = ser.readline()
            i = i + 1
            # Decode the data from bytes to a string
            decoded_data = data.decode('utf-8')

            # Split the data into individual values
            values = decoded_data.strip().split(',')

            # Check if the data contains all the expected values
            if len(values) >= 4:
                no2, c2h5ch, voc, co = values[:4]
                csv_writer.writerow([no2, c2h5ch, voc, co, data_name])
            else:
                print(f"Incomplete data: {decoded_data}")

            time.sleep(1 / read_frequency)

    except KeyboardInterrupt:
        # Handle Ctrl+C to exit the program
        print("Serial reader terminated.")

    finally:
        ser.close()
