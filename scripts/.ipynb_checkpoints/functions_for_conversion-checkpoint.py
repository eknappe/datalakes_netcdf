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

#Import the instrument metadata file
imeta_loc = "\\Users\\knappeel\\Documents\\datalakes\\data_convert\\data\\input\\instument_metadata.txt"

#Load in the file
imetadata = pd.read_csv(imeta_loc, sep =',', header = 0)
    
#Input from user

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

#What is your date/time column(s) named? Ordered from largest to smallest (e.g. Date, Time OR Year, Month, Day)
time_columns = ['Time']

#Do your data files collect data in UTC time? If no, enter the time shift in hours:
time_shift = 0

#What are the variable names in the data files (include the time/date columns)? Only include ones you are interested in:
var_names = ['Time', 'Temp']

#Create a variable mapping file:
var_output = '\\Users\\knappeel\\Documents\\datalakes\\data_convert\\data\\input\\variables.csv'

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
        
    
print(f"\nCSV written: '{var_output}'")
print("\nATTENTION: Fill in the csv with the needed variable information")
print("\nSEE README for additional information")


## Get all the data

#Folder with data (can be within folders within this folder)
base_folder = "\\Users\\knappeel\\Documents\\datalakes\\data_convert\\data\\input\\L0\\"

#Assumes the data files have the serial_id within, if different naming add here 
target_serial_id = imetadata.serial_id.to_list()

#File pattern, if exists (where {serial} is the from the list from imetadata)
data_file_pattern = "*{serial}*_data.txt"


#find the path to all the data files
def find_files(base_folder, target_serial_ids, file_pattern):
    
    #pattern not provided then use look for the serial number
    if not file_pattern:
        file_pattern = '*{serial}*'
    
    base_path = Path(base_folder)
    found_files = []
    
    #double check that folder exists
    if not base_path.exists():
        print(f"Warning: folder does not exist: {base_folder}")
        return found_files
    
    #search all files recursively
    for file_path in base_path.rglob("*"):
        if not file_path.is_file():
            continue
        
        for target_serial in target_serial_ids:
            expected_name = file_pattern.replace('{serial}', str(target_serial))
            if fnmatch.fnmatch(file_path.name, expected_name):
                found_files.append((file_path, target_serial))
                break
    print(f"Total files found: {len(found_files)}")
    return found_files

found_data_files = find_files(base_folder, target_serial_id, data_file_pattern)      


#combine mutliple time columns
def combine_date_time(df, column_names, seperator = ' '):
    
    #copy of dataframe
    df_copy = df.copy()
    
    #do the columns exist
    missing_cols = [col for col in column_names if col not in df_copy.columns]
    if missing_cols:
        raise ValueError(f"\nThe following columns were not found: {missing_cols}. Please check data file format.")
    
    if len(column_names) == 1:
        #just one time column, score
        combined_column = df_copy[column_names[0]].astype(str)
    else:
        #multiple columns, eek, start us off
        combined_column = df_copy[column_names[0]].astrype(str)
        #loop it and smush them together
        for col in column_names[1:]:
            combined_column = combined_column + seperator + df_copy[col].astype(str)
    
    #parse the data
    datetime_series = None
    
    try:
        datetime_series = pd.to_datetime(combined_column, infer_datetime_format = True)
        print('yay pasring complete - delete after testing')
    #didnt work, let the user know
    except Exception as e:
        print('Trouble formatting your date/time column(s). Please double check you entered the correct date/time column names.')
        
    #convert to seconds since 1970-01-01
    epoch_seconds = datetime_series.astype('int64') // 10**9
    
    #drop the original date/time columns that were combined
    df_copy = df_copy.drop(columns = column_names)
    
    #add back in the new datetime column
    df_copy['time'] = epoch_seconds

    return df_copy

#function to handle time offsets (want everything in utc time)
def apply_time_correction(df, hour_offset):
    if hour_offset > 0:
        df['time'] = df['time'] + pd.to_timedelta(hour_offset, unit = 'h')
    
    return df















