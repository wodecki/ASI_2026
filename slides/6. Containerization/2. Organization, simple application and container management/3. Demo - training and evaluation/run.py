import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle

# ------- READING DATA -------
# Read input data
print('... reading data ...')
df = pd.read_csv('data/data_init.csv')

# Save the data
print('... saving data ...')
df.to_csv('data/data_train.csv', index=False)

import pandas as pd

# ------- TRAINING -------
# Read training data
df = pd.read_csv('data/data_train.csv')

# Reshape data for modelling
X = df['x'].values.reshape(-1,1)
y = df['y'].values.reshape(-1,1)

# Instatiate the model
our_model = LinearRegression()

# Fit the model
print('... trainig ...')
our_model.fit(X, y)

'''
# Print coefficient
print('y = a*x + b')
print('a = ', our_model.coef_[0][0])
print('b = ', our_model.intercept_[0])
'''

# Export the model
print('...Exporting the model...')
pickle.dump(our_model, open('model/model_1.0.pkl', 'wb'))

# ------- EVALUATION -------

from sklearn.metrics import mean_squared_error, r2_score
from datetime import date, datetime

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Load model
model = pickle.load(open("model/model_1.0.pkl", 'rb'))

# Read test data
test_data = pd.read_csv("data/data_test.csv")

X = test_data['x'].values.reshape(-1,1)
y = test_data['y'].values.reshape(-1,1)

# Predict
predictions = model.predict(X)

# Evaluate
RMSE = np.sqrt(mean_squared_error(y, predictions))
r2 = r2_score(y, predictions)
print('RMSE on test data: ', RMSE)
print('r2 on test data: ', r2)

# Save the evaluation data
eval_df = pd.DataFrame()

now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# Create new rows as separate DataFrames
new_row1 = pd.DataFrame({'time_stamp':[now], 'version':['1.0'], 'metric':['RMSE'], 'score':[RMSE]})
new_row2 = pd.DataFrame({'time_stamp':[now], 'version':['1.0'], 'metric':['r2'], 'score':[r2]})

# Concatenate the DataFrames
eval_df = pd.concat([eval_df, new_row1, new_row2], ignore_index=True)

print('... saving evaluation ...')
eval_df.to_csv('evaluation/model_eval.csv', index=False)