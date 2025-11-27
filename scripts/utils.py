#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 14:16:36 2025

@author: knappeel
"""

from pathlib import Path
import fnmatch
from datetime import datetime
import pandas as pd


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
