## Convert text files to netCDF formats

The purpose of this script is to help people who are new to using netCDFs, convert their data into a netCDF format. This script was written to help users upload their data to the Datalakes platform (https://www.datalakes-eawag.ch/?home) , but is generic enough that it can be used for other purposes. 

### What is a netCDF?

A netCDF (Network Common Data Format) is a file format that is very effecient for storing and sharing multi-dimensional data. The files are also capable of storing metadata so they are self-describing. The data is stored in a series of arrays that makes it easy to extract portions of the data (without reading in the entire file) and append additional data.

Examples of how dat can be stored in netCDFs:

Three-dimensional data (e.g. temperature over an area varying with time)
![Alt text](https://gitlab.eawag.ch/ellen.knappe/datalake-netcdf/-/blob/main/images/netcdf_2.pdf "3d_netcdf")




### Components of a netCDF 







### Additional netCDF resources

The unidata NetCDF user's guide: https://docs.unidata.ucar.edu/nug/current/index.html#netcdf_purpose

