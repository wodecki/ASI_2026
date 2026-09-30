import pandas as pd
import random

import os

print('... App 2 Started ...\n')

script_dir = os.path.abspath( os.path.dirname( __file__ ) )
parent = os.path.dirname(script_dir)

input_path = os.path.join(parent, 'app_1/output/output_1.csv')

if os.path.isfile(input_path):
    df = pd.read_csv(input_path, header = None)
else:
    df = pd.DataFrame([[2, 43, 510], [3, 4, 315]])
    df.to_csv(input_path, index = False, header = False)

df = pd.read_csv(input_path, header = None)
print('Original df:')
print(df)

n = random.randint(1,5)

print('\nRandom number: ', n)

df_out = df + n


output_path = os.path.join(script_dir, 'output/output_2.csv')

df_out.to_csv(output_path, header=False, index=False)


print("")
print('Transformed df:')
print(df_out)

print('... App 2 Completed ...\n')