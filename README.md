# canada-climate-python

A script for extracting daily and monthly values for Environment Canada stations and outputting a handful of calculated metrics

_A work in progress: run at your own risk_ 

---
## Features

- Downloading of weather station data using the Environment Canada FTP (<ftp://ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Readme.txt>) and wget. 

- Outputting of continuous station data according to date/time for several environmental indicators for Hourly and Daily data.

- Graphical output of variables using numpy and matplotlib.

## Requires

Python3
- collections, ftplib, matplotlib, numpy, pandas, wget

## Goals

- Automatic downloading of nearest station data to point of interest or boundary box (will require geoprocessing tools)
- Outputting of new data frames as SQL-loadable databases (Further research needed)
- ~~Outputting of daily data subplot figures based on number of years collected~~
- ~~Selectable years for daily data sets~~

