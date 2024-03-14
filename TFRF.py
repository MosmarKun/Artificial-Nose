'''
Please install this libraries before progressing as this libraries are not pre-installed on
Google Collab

!pip install wurlitzer
!pip install -q -U tensorflow_decision_forests
'''
#Importing the Libraries
import numpy as np
import pandas as pd
import math
import tensorflow as tf
import tensorflow_decision_forests as tfdf
import joblib
from joblib import Parallel, delayed
import matplotlib.pyplot as plt


#Load the training dataset from .csv file  also in this same directory
train_df = pd.read_csv('/content/outputtraining.csv')
print(train_df.head(5))
print()
print()

#Load the test dataset from .csv file  also in this same directory
test_df = pd.read_csv('/content/outputtesting.csv')
print(test_df.head(5))
print()
print()

#Since keras do not accept strings as labels we are going to encode our labels
#and make them integer for the training process

#Our column was named Labels
labels = "Labels"

y_labels = train_df[labels].unique().tolist()
print()
print("-------------------------------------------------------------------------------------------------------------")
print(f"Label classes: {y_labels}")
print("--------------------------------------------------------------------------------------------------------------")

train_df[labels] = train_df[labels].map(y_labels.index)


#Repeat the above processes for the test dataset
yt_labels = test_df[labels].unique().tolist()
print()
print("-==============================================================================================================")
print(f"Label classes: {yt_labels}")
print("-===============================================================================================================")

test_df[labels] = test_df[labels].map(yt_labels.index)
print()
print("##############################################################################################################")
print("{} examples in training sets, {} examples in test sets.".format(len(train_df), len(test_df)))
print("##############################################################################################################")


#prediction dataset
pred_df = pd.read_csv('/content/outputtesting.csv')
print()
print(pred_df.head(5))

X_pred = pred_df.iloc[:, :-1]

#converting the pandas Dataframe to tensorflow dataset
train_ds = tfdf.keras.pd_dataframe_to_tf_dataset(train_df, label=labels)
test_ds = tfdf.keras.pd_dataframe_to_tf_dataset(test_df, label=labels)
pred_ds = tfdf.keras.pd_dataframe_to_tf_dataset(X_pred)

#let train a Random forest model
#First let define the model
model_RF = tfdf.keras.RandomForestModel(task=tfdf.keras.Task.CLASSIFICATION, verbose=2)

#let train the model
model_RF.fit(train_ds)


#Evaluating the model
model_RF.compile(metrics=["accuracy"])
model_eval = model_RF.evaluate(test_ds, return_dict=True)
print()
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
for name, value in model_eval.items():
    print(f"{name}: {value:.4f}")


print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

'''
To visualize the tree use this code, but this only limited to Google Colab
tfdf.model_plotter.plot_model_in_colab(model_RF, tree_idx=3, max_depth=30,)
'''