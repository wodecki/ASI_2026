import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle

# Read data
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