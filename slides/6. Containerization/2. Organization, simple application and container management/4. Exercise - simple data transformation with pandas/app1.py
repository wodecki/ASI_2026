import pandas as pd
import os

df = pd.read_csv('input/input.csv', header = None)

df_out = 2*df

df_out.to_csv('output/output.csv', header = False, index = False)

print(df_out)