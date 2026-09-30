import pandas as pd
import os
import subprocess

script_dir = os.path.abspath( os.path.dirname( __file__ ) )
program_1_path = os.path.join(script_dir, 'app_1/app_1.py')
program_2_path = os.path.join(script_dir, 'app_2/app_2.py')

program_list = [program_1_path, program_2_path]

for program in program_list:
    subprocess.call(['python', program])
