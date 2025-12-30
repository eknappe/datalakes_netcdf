#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 14:33:09 2025

@author: knappeel
"""


import os
import pandas as pd
from pathlib import Path
import netCDF4 as nc

### script to view the netcdf file

### Set working directory -- python scripts are hosted in within a folder in this directory
### Going to be two folders in horizontal -- data and python
working_directory = Path(__file__).parent.parent.resolve()
data_directory = working_directory / 'data'


#Import the instrument metadata file
netcdf_loc = data_directory / 'input/test_netcdfs/L1_Greifensee_CTD_W_20200629_000000.nc'

ds = nc.Dataset(netcdf_loc)