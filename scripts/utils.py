#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 14:16:36 2025

@author: knappeel
"""

import re
from pathlib import Path
import fnmatch
from datetime import datetime
import pandas as pd
from collections import defaultdict


#find all the unique identifiers so user doesnt have to list them all
def extract_identifier_from_pattern(filename, file_pattern):
    """
    Find the identifier from the filename based on the user provide pattern with {idvalue}.

    Pattern examples:
    - 'lakelugano_{idvalue}meters.txt' -> extracts whats in {idvalue} position
    - 'lakelugano_20meters.tif' -> no idvalue, so returns full filename without extension
    - 'experiment_{idvalue}_*.csv' -> extracts idvalue
    - '*.txt' -> returns full filename

    """

    #check if pattern contains {idvalue}
    if '{idvalue}' in file_pattern:
        # convert the pattern to regex
        regex_pattern = re.escape(file_pattern)

        # replace {idvalue} with a capture group (e.g. this is what we want to exctract)
        regex_pattern = regex_pattern.replace(r'\{idvalue\}', r'(.+?)')

        # replace wildcard (*) with non-capture
        regex_pattern = regex_pattern.replace(r'\*', r'.+?')

        # match the pattern
        match = re.match(regex_pattern, filename)

        if match:
            return match.group(1) #return the captured idvalue

    #if not {idvalue} in pattern, then use full filename without extension as identifier
    return filename.rsplit('.', 1)[0] if '.' in filename else filename

def find_file(base_folder, file_pattern):
    """
    find all the files within the folder
    list all the unique identifiers

    args:
        base_folder: path to folder to search for the data
        file_pattern: pattern with {idvalue} placeholder

    return:
        metadata: dictionary with identifier as key and list of file paths as values
        summary: dictionary with count and unique identifiers
    """
    base_path = Path(base_folder)

    if not base_path.exists():
        print(f"Warning: folder does not exist: {base_folder}")
        return {}, {}

    # create dictionary to be filled
    metadata = defaultdict(list)
    all_files = []

    # create a glob pattern from file_pattern (replace {idvalue} and other {} with *)
    glob_pattern = re.sub(r'\{[^}]+\}', '*', file_pattern)

    # search for files using glob pattern
    for file_path in base_path.rglob(glob_pattern):
        if not file_path.is_file():
            continue

        # exctract identifier based on the pattern
        identifier = extract_identifier_from_pattern(file_path.name, file_pattern)

        if identifier:
            all_files.append(file_path)
            metadata[identifier].append(file_path)

    # put all the info together
    summary = {
        'total_files': len(all_files),
        'unique_identifiers': list(metadata.keys()),
        'identifier_count': len(metadata),
        'files_per_identifier': {k: len(v) for k, v in metadata.items()}
        }

    print(f"Total files found: {summary['total_files']}")
    print(f"Total number of unqiue 'idvalues' found: {len(summary['unique_identifiers'])}")

    return metadata, summary

def sanitize_name(name):
    """
    Just remove any spaces in the names and replace with underscores cause its easier to deal with
    """
    return name.replace(' ', '_')


# combine mutliple time columns
def combine_date_time(df, column_names, seperator = ' '):

    # copy of dataframe
    df_copy = df.copy()

    # do the columns exist?
    missing_cols = [col for col in column_names if col not in df_copy.columns]
    if missing_cols:
        raise ValueError(f"\nThe following columns were not found: {missing_cols}. Please check data file format.")

    if len(column_names) == 1:
        # just one time column, score
        combined_column = df_copy[column_names[0]].astype(str)
    else:
        # multiple columns, eek, start us off
        combined_column = df_copy[column_names[0]].astype(str)
        # loop it and smush them together
        for col in column_names[1:]:
            combined_column = combined_column + seperator + df_copy[col].astype(str)

    # parse the data
    datetime_series = None

    try:
        datetime_series = pd.to_datetime(combined_column)

    # didnt work, let the user know
    except Exception as e:
        print('Trouble formatting your date/time column(s). Please double check you entered the correct date/time column names.')

    # convert to seconds since 1970-01-01
    epoch_seconds = datetime_series.astype('int64') // 10**9

    # drop the original date/time columns that were combined
    df_copy = df_copy.drop(columns = column_names)

    # add back in the new datetime column
    df_copy['time'] = epoch_seconds

    return df_copy

def files_to_process(base_folder, data_file_pattern, file_identifiers):
    """ find all the files which we want to process
    then create a list so we can cycle through them
    args:
        base_folder: path to the folder where data are collected
        data_file_pattern: how the data files are named, so we only grab those and not other information
        file_indentifiers: data frame that includes the file ids (col0), number of file (col1) and dim1 values (col2)
    returns:
        a list of the file locations
    """
    if not base_folder.exists():
        print(f"Warning: folder does not exist: {base_folder}")
        return {}, {}

    # going to replace the idvalue with a wildcard since it will already only look for the identifiers
    broad_pattern = data_file_pattern.replace("{idvalue}", "*")
    
    # collect all matching files into a dataframe
    found_files = pd.DataFrame([str(f) for f in Path(base_folder).rglob(broad_pattern) if f.is_file()], columns = ['file_path'])
    
    #nada?
    if found_files.empty:
        print("Warning: no files found. Please check datafile_information.csv")
        return pd.DataFrame()
    
    # we want to include the dim1 values with their associated files
    # so a bit of tinkering so we can merge the dataframes
    id_dim1 = file_identifiers.iloc[:,[0,2]].copy()
    id_dim1.columns = ['identifier', 'dim1']
    id_dim1['identifier'] = id_dim1['identifier'].astype(str)
    
    # extract the identifer for the file path
    # check the file path for the id
    found_files['identifier'] = found_files['file_path'].apply(lambda fp: next((id for id in id_dim1['identifier'] if id in fp), None))
    
    # merge to attach dim1 values
    result = found_files.dropna(subset=['identifier']).merge(id_dim1, on = 'identifier', how = 'left')

    return result[['file_path', 'dim1']].reset_index(drop=True)


def files_to_process_1d(base_folder, data_file_pattern):
    """ same as above but just for 1d data cause more simple"""
    if not base_folder.exists():
        print(f"Warning: folder does not exist: {base_folder}")
        return {}, {}

    file_list = [str(f) for f in base_folder.rglob(data_file_pattern) if f.is_file()]

    if not file_list:
        print("Warning no files found. Check folder path and file pattern.")
        return []
    
    print(f"Total files found: {len(file_list)}")
    return file_list


