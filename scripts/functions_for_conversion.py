# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 10:06:21 2025

@author: knappeel

Data to netCDF converter for Datalakes platform
"""


import os
import pandas as pd
import numpy as np
import xarray as xr
import csv
import json
from pathlib import Path
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import fnmatch

### Set working directory -- python scripts are hosted in within a folder in this directory
### Going to be two folders in horizontal -- data and python
working_directory = Path(__file__).parent.parent.resolve()
data_directory = working_directory / 'data'
output_directory = data_directory / 'output'

#Import the instrument metadata file
imeta_loc = data_directory / 'input/instrument_metadata.txt'

#Load in the file
imetadata = pd.read_csv(imeta_loc, sep =',', header = 0)
    
#####Input from user

#Data collection (YYYY,mm,dd,hh,min,ss):
start_time = datetime(2025,1,17,0,0,0)    
end_time =  datetime(2025,4,22,0,0,0)
                
#Convert start and end time to seconds since 1970 for netcdf 
sec_start_time = start_time.timestamp()
sec_end_time = end_time.timestamp() 

##Information on your data files

#Do your data files have headers? How many lines of header (we will skip those to the data)?
skiprows = 1

#What is the seperator in your data file?
seperator = ','

#What is your date/time column(s) named? Ordered from largest to smallest (e.g. Date, Time OR Year, Month, Day, etc.)
time_columns = ['Time']

#Do your data files collect data in UTC time? If no, enter the time shift in hours:
time_shift = 0

#What are the variable names in the data files (include the names of the time/date columns)? Only include ones you are interested in:
var_names = ['Time', 'Temp']

#Create a variable mapping file:
var_output = data_directory / 'input/variables.csv'

#Do not edit the below:
headers = ['var_name', 'dim', 'unit', 'long_name', 'min', 'max']

#input the time metadata that we already know
time_metadata = {'var_name':'time',
                 'dim': 'time',     #var is dependent on this variable
                 'unit': 'seconds since 1970-01-01 00:00:00',
                 'long_name': 'time',
                 'min': sec_start_time - 86400,
                 'max': sec_end_time + 86400}

# with open(var_output, mode = 'w', newline='') as file:
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()
    
#     #write time 
#     writer.writerow(time_metadata)
    
#     #manage the overlapping time entries if they exist
#     list3 = [item for item in var_names if item not in time_columns]
    
#     #write in the other variables
#     for name in list3:
#         row = {
#             'var_name': name.lower(),
#             'dim':'',
#             'unit': '',
#             'long_name': '',
#             'min':'',
#             'max': ''}
#         writer.writerow(row)
        
    
print(f"\nVariable CSV written: '{var_output}'")
print("\nATTENTION: Fill in the csv with the needed variable information")
print("\nSEE README for additional information")


## Get all the data

#Folder with data (can be within folders within this folder)
base_folder = data_directory / 'input/L0/'

#Assumes the data files have the serial_id within, if different naming add here 
target_serial_id = imetadata.iloc[:,0].to_list()

#File pattern, if exists (where {serial} is the from the list from imetadata)
data_file_pattern = "*{serial}*_data.txt"


found_data_files = find_files(base_folder, target_serial_id, data_file_pattern)   












