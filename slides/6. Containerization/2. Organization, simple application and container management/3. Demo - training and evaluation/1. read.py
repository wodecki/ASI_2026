import pandas as pd

# Read data
print('... reading data ...')
df = pd.read_csv('data/data_init.csv')

# Save the data
print('... saving data ...')
df.to_csv('data/data_train.csv', index=False)