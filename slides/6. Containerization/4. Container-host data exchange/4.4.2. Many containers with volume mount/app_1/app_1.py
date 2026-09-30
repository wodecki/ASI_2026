import pandas as pd
import random
import os

print('... App 1 Started ...\n')

input_path = 'data/input_1.csv'

if os.path.isfile(input_path):
    df = pd.read_csv(input_path, header = None)
else:
    df = pd.DataFrame([[1, 32, 10], [3, 4, 315]])
    df.to_csv(input_path, index = False, header = False)

df = pd.read_csv(input_path, header = None)
print('Original df:')
print(df)

n = random.randint(1,5)

print('\nRandom number: ', n)

df_out = n*df

output_path = 'data/output_1.csv'
df_out.to_csv(output_path, header=False, index=False)


print("")
print('Transformed df:')
print(df_out)

print('\n... App 1 Completed ...\n')