import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import joblib
import os

def format_percentage(value):
    return f"{value:.2f}%".zfill(6)

def format_matrix_value(value):
    return f"{value:.2f}%".rjust(10)

def format_data_name(name):
    return name[:10].ljust(10)

# Load the data from the CSV file
data = pd.read_csv('outputtraining.csv')

# Shuffle the data
data = data.sample(frac=1, random_state=42).reset_index(drop=True)

# Split the data into features and labels
X = data.iloc[:, :-1].values
y = data.iloc[:, -1].values

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define different configurations of MLPs
mlp_configurations = [
    {'hidden_layers': (3,), 'max_iter': 10000, 'random_state': 42},
    {'hidden_layers': (10, 5), 'max_iter': 10000, 'random_state': 42},
    {'hidden_layers': (4, 60, 30, 20, 15, 11), 'max_iter': 10000, 'random_state': 42},
]

# Create a file named "MLP.txt" to save the results
with open("MLP.txt", "w") as file:
    for config in mlp_configurations:
        hidden_layers = config['hidden_layers']
        max_iter = config['max_iter']
        random_state = config['random_state']   

        # Create the MLP classifier and train it using the training data
        mlp = MLPClassifier(hidden_layer_sizes=hidden_layers, max_iter=max_iter, random_state=random_state)
        mlp.fit(X_train, y_train)

        # Predict the classes for the testing data
        y_pred = mlp.predict(X_test)

        # Calculate the accuracy of the classifier
        accuracy = accuracy_score(y_test, y_pred)

        # Format and write the results to the file
        hidden_layers_str = str(hidden_layers).replace("(", "").replace(")", "")
        accuracy_str = format_percentage(accuracy*100)
        result_str = f"Configuration: {hidden_layers_str}, Accuracy: {accuracy_str}\n"
        file.write(result_str)
        print(result_str)

        # Create and format the confusion matrix
        conf_matrix = confusion_matrix(y_test, y_pred)
        file.write("Confusion Matrix (Percentages):\n")
        header = " " * 13 + " | ".join([format_data_name(name) for name in data['Data Name'].unique()]) + "\n"
        file.write(header)
        for i, data_name in enumerate(data['Data Name'].unique()):
            row = [format_data_name(data_name)]
            for j, target_name in enumerate(data['Data Name'].unique()):
                accuracy_percent = (conf_matrix[i][j] / conf_matrix[i].sum()) * 100
                row.append(format_matrix_value(accuracy_percent))
            file.write(" | ".join(row) + "\n")

print("Results saved to 'MLP.txt'.")
