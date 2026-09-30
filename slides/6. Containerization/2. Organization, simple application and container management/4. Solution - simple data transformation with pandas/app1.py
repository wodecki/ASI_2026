import pandas as pd
import os.path

print('Pandas version: ', pd.__version__, '\n')
df = pd.read_csv('input/input.csv', header = None)
print('Original df:')
print(df)

df_out = 2*df
output_path = 'output/output.csv'
if os.path.isfile(output_path):
        df_out.to_csv(output_path, mode='a', header=False, index=False)
else:
    df_out.to_csv(output_path, index=False)

print("")
print('Transformed df:')
print(df_out)