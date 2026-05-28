# Convert text files to netCDF formats

The purpose of this script is to help people who are new to using netCDFs, convert their data into a netCDF format. This script was written to help users upload their data to the Datalakes platform (https://www.datalakes-eawag.ch/?home), but is generic enough that it can be used for other purposes. 

This script was developed to help walk through the process of converting data files into netCDF format. It is meant to be general enough to work on various types of data, so it will require some input of information and stepping through the notebook carefully. The code was commented to help follow along. 

## Which script to use:

1d_csv_to_netCDF.ipynb = meteostations, and other measurements that are taken at a single location through time
2d_csv_to_netCDF.ipynb = bouys, thermister chains, and other measurements taken at different depths/water pressures/... through time
    *If each data file contains only a singular dimension value (e.g. all at a single depth), use option A
    *If each data file contains multiple dimension values (e.g multiple depths, multiple pressure values), use option B

See netCDF_README.md for more information about dimensions in netCDFs. 

## How to use:

To use this file, ensure that you have all the necessary python libraries installed. 

If you use homebrew, create a new virtual environment and install the necesary libraries:
```
python3 -m venv ~/python-envs/projectname
source ~/python-envs/projectname/bin/activate
pip install -r requirements.txt
```

If you use conda users, create a new environment. 
```
conda env create -f environment.yml
conda activate 
```


## Understanding components of the code

* Step 1:
    * File naming conventions: For this we want to make sure we are pulling the information from the files correctly. This means indicating where in the file name the identifier is. The identifier can be the dimension value or identifier that is linked to the dimension value (e.g. the serial number of the instrument). For example, if your files look like this:
        
        **Example 1.** lakelugano_exo_15m_2403071055.csv & lakelugano_exo_15m_2507010310.csv & so on ... in this case the number preceeding the m is actually the depth (dimension value). The second is date format. Thus we want all the different date files, so we will use a wildcard to capture all the different dates. 
        
        *SOLUTION:* 'lake_lugano_exo_{idvalue}m_*.csv' (more specific, generally better)
        
        *ALTERNATIVE:* '*_{idvalue}m_ *.csv' (less specific, this could also grab lake_zurich_exo_10m_.csv files, or lake_lugano_max_20m_.csv files, which might not be what you want)
        
        **Example 2.** AUTO_200579_20250424_1602_data.txt & AUTO_200579_20250425_1602_data.txt & so on... in this case, the first number is a serial number of the instrument, and the instrument is measuring variables at a specific depth. The second number is the date, and the third number is another identifier. Since we want all the files for the different dates, we will use a wildcard which will also allow us to not have to define the third number. 
        
        *SOLUTION:* 'AUTO_{idvalue}_*_data.txt'
        
        *ALTERNATIVE:* 'AUTO_{idvalue}_* _*_data.txt'
        
        **Example 3.** If your files don't follow any naming convention, just indicate the file extension. This will grab all the files within the folder. This is not recommended because it will require a lot of work. 
        
        *SOLUTION:* '*.txt' or '*.csv'
        
        
        **WHY:** The * is like a wild card. The way the scripts works, it will look for files with the above patterns. For example, in solution 1 if the file is a .txt it will not read in the file. So use the * where needed, but best to be as specific as possible or it could grab files that are not data files. 
        
* Step 5:
    * Setting the dimensions for variables: The dimensions are like the axes of your data and are shared across your variables (if you have multiple). 
        * For example: if you have water temperature data measured at 10 depths through time, the water temperature would have dim = (time, depth). If you are measuring mulitple variables (e.g. water temp, salinity, conductivity) at multiple depths through time, then the dim for every variable are dim = (time, depth). 
        * It is also possible to have the above, as well as say mixing_depth or thermocline depth or heat content, which would only be dependent on time but not depth, within the same netcdf file. Thus these variable would have dim = (time,).
        * Another example: If you have salinity measured over a spatial are through time, dim = (time, latitude, longitude). 

    * Each dimension will also have a variable associated with it that list the values of the dimension, so called the coordinate variables. Thus, time would have the dim = (time, ), and if your other dimension is depth, then dim = (depth,).
    
        

        
        
