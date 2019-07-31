import pandas as pd
import glob
import xarray as xr
import numpy as np


# Searches /dmf2 for the station, then calls the needed scripts to read and assemble the data.
def find_and_extract_dly(station, rm_flags=False):

    # REQUIRED PARAMETERS
    # station: dict containing the attributes 'name' and 'province'  ---  'name' does not need to be exact, but should be unique within the province

    # OPTIONAL PARAMETERS
    # rm_flags: boolean  ---  removes all the 'Flag' columns of the ECCC files

    # Find the OBS station in our database
    path_obs = 'path/to/the/csv/folders/'
    station_files = sorted(glob.glob(path_obs + '**/*.csv'))

    # extract the .csv data
    station = read_multiple_eccc_dly(station_files, rm_flags=rm_flags)

    return station


# Uses xarray to transform the ECCC daily stations into a netCDF file
def dly_to_netcdf(station, path_output):

    # REQUIRED PARAMETERS
    # station: dict created by using find_and_extract_dly
    # path_output: string  ---  path where to save the data

    # first, transform the Date/Time to a 'days since' format
    time = station['data']['Date/Time'] - np.array('1950-01-01T00:00', dtype='datetime64')
    time = time.astype('timedelta64[s]').astype(float) / 86400

    # we use expand_dims twice to 'add' longitude and latitude dimensions to the station data
    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Mean Temp (°C)'] + 273.15, axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'tas'
    da.attrs['standard_name'] = 'air_temperature'
    da.attrs['long_name'] = 'Near-Surface Air Temperature'
    da.attrs['units'] = 'K'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Mean Temp (°C)'

    # for the first variable, we simply create a dataset from it
    ds = da.to_dataset()

    # import the other variables
    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Max Temp (°C)'] + 273.15, axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'tasmax'
    da.attrs['standard_name'] = 'air_temperature maximum'
    da.attrs['long_name'] = 'Daily Maximum Near-Surface Temperature maximum'
    da.attrs['units'] = 'K'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Max Temp (°C)'
    ds['tasmax'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Min Temp (°C)'] + 273.15, axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'tasmin'
    da.attrs['standard_name'] = 'air_temperature minimum'
    da.attrs['long_name'] = 'Daily Maximum Near-Surface Temperature minimum'
    da.attrs['units'] = 'K'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Min Temp (°C)'
    ds['tasmin'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Heat Deg Days (°C)'], axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'hdd'
    da.attrs['standard_name'] = 'heating_degree_days'
    da.attrs['long_name'] = 'Number of Degrees Celsius Under a Mean Temperature of 18 °C'
    da.attrs['units'] = 'C'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    ds['hdd'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Cool Deg Days (°C)'], axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'cdd'
    da.attrs['standard_name'] = 'cooling_degree_days'
    da.attrs['long_name'] = 'Number of Degrees Celsius Over a Mean Temperature of 18 °C'
    da.attrs['units'] = 'C'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    ds['cdd'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Total Rain (mm)'] / 86400, axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'prlp'
    da.attrs['standard_name'] = 'rainfall_flux'
    da.attrs['long_name'] = 'Liquid Precipitation'
    da.attrs['units'] = 'kg m-2 s-1'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Total Rain (mm) using a density of 1000 kg/m³'
    ds['prlp'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Total Snow (cm)'] / 86400, axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'prsn'
    da.attrs['standard_name'] = 'snowfall_flux'
    da.attrs['long_name'] = 'Snowfall Flux'
    da.attrs['units'] = 'kg m-2 s-1'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Total Snow (cm) using a density of 100 kg/m³'
    ds['prsn'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Total Precip (mm)'] / 86400, axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'pr'
    da.attrs['standard_name'] = 'precipitation_flux'
    da.attrs['long_name'] = 'Precipitation'
    da.attrs['units'] = 'kg m-2 s-1'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Total Precip (mm) using a density of 1000 kg/m³'
    ds['pr'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Snow on Grnd (cm)'] / 100, axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'snd'
    da.attrs['standard_name'] = 'surface_snow_thickness'
    da.attrs['long_name'] = 'Snow Depth'
    da.attrs['units'] = 'm'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Snow on Grnd (cm)'
    ds['snd'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Dir of Max Gust (10s deg)'], axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'sfcWindmax_dir'
    da.attrs['standard_name'] = 'wind_gust_from_direction maximum'
    da.attrs['long_name'] = 'Direction from which the Daily Maximum Near-Surface Gust Wind Speed maximum Blows'
    da.attrs['units'] = 'degree'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Dir of Max Gust (10s deg)'
    ds['sfcWindmax_dir'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['data']['Spd of Max Gust (km/h)'] / 3.6, axis=1), axis=2),
                      [('time', time), ('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'sfcWindmax'
    da.attrs['standard_name'] = 'wind_speed_of_gust maximum'
    da.attrs['long_name'] = 'Daily Maximum Near-Surface Gust Wind Speed maximum'
    da.attrs['units'] = 'm s-1'
    da.attrs['grid_mapping'] = 'regular_lon_lat'
    da.attrs['comments'] = 'station data converted from Spd of Max Gust (km/h)'
    ds['sfcWindmax'] = da

    # add attributes to lon, lat, time, elevation, and the grid
    da = xr.DataArray(np.full(len(time), np.nan), [('time', time)])
    da.name = 'regular_lon_lat'
    da.attrs['grid_mapping_name'] = 'lonlat'
    ds['regular_lon_lat'] = da

    da = xr.DataArray(np.expand_dims(np.expand_dims(station['elevation'], axis=1), axis=2),
                      [('lat', [station['latitude']]), ('lon', [station['longitude']])])
    da.name = 'elevation'
    da.attrs['standard_name'] = 'elevation'
    da.attrs['long_name'] = 'elevation'
    da.attrs['units'] = 'm'
    da.attrs['axis'] = 'Z'
    ds['elevation'] = da
    ds = ds.set_coords('elevation')

    ds.lon.attrs['standard_name'] = 'longitude'
    ds.lon.attrs['long_name'] = 'longitude'
    ds.lon.attrs['units'] = 'degrees_east'
    ds.lon.attrs['axis'] = 'X'

    ds.lat.attrs['standard_name'] = 'latitude'
    ds.lat.attrs['long_name'] = 'latitude'
    ds.lat.attrs['units'] = 'degrees_north'
    ds.lat.attrs['axis'] = 'Y'

    ds.time.attrs['standard_name'] = 'time'
    ds.time.attrs['long_name'] = 'time'
    ds.time.attrs['units'] = 'days since 1950-01-01 00:00:00'
    ds.time.attrs['axis'] = 'T'
    ds.time.attrs['calendar'] = 'gregorian'

    # add global attributes
    ds.attrs['Station Name'] = station['name']
    ds.attrs['Province'] = station['province']
    ds.attrs['Climate Identifier'] = station['ID']
    ds.attrs['WMO Identifier'] = station['WMO_ID']
    ds.attrs['TC Identifier'] = station['TC_ID']
    ds.attrs['Institution'] = 'Environment and Climate Change Canada'

    # save the data
    ds.to_netcdf(path_output + ds.attrs['Station Name'] + '.nc')


##########################################
# BELOW THIS POINT ARE UTILITY SCRIPTS
##########################################


# This calls read_single_eccc_dly and appends the data in a single Dict
# This is used for a single station! Do not send multiple stations in the 'files' list!
def read_multiple_eccc_dly(files, rm_flags=False):

    # REQUIRED PARAMETERS
    # files: a list of all the files to append

    # OPTIONAL PARAMETERS
    # rm_flags: boolean  ---  removes all the 'Flag' columns of the ECCC files

    # Extract the data for each files
    station_meta = None
    datafull = None
    for f in range(len(files)):
        station_meta, data = read_single_eccc_dly(files[f])
        if f == 0:
            datafull = data
        else:
            datafull = datafull.append(data, ignore_index=True)

    # change the Date/Time column to a datetime64 type
    datafull['Date/Time'] = pd.to_datetime(datafull['Date/Time'])

    # if wanted, remove the quality and flag columns
    if rm_flags:
        index_quality = [i for i, s in enumerate(datafull.columns.values) if 'Quality' in s]
        datafull = datafull.drop(datafull.columns.values[index_quality], axis='columns')
        index_flag = [i for i, s in enumerate(datafull.columns.values) if 'Flag' in s]
        datafull = datafull.drop(datafull.columns.values[index_flag], axis='columns')

    # combine everything in a single Dict
    station = station_meta
    station['data'] = datafull

    return station


# This is the script that actually reads the CSV files. The metadata are saved in a Dict, while the data is returned as a pandas Dataframe
def read_single_eccc_dly(file):

    # REQUIRED PARAMETERS
    # file: a string containing the file to be read

    # Read the whole file
    fi = open(file, "r")
    lines = fi.readlines()
    fi.close()

    # Find each elements in the header
    search_header = [0] * 9
    search_header[0] = [i for i, s in enumerate(lines) if 'Station Name' in s][0]
    search_header[1] = [i for i, s in enumerate(lines) if 'Province' in s][0]
    search_header[2] = [i for i, s in enumerate(lines) if 'Latitude' in s][0]
    search_header[3] = [i for i, s in enumerate(lines) if 'Longitude' in s][0]
    search_header[4] = [i for i, s in enumerate(lines) if 'Elevation' in s][0]
    search_header[5] = [i for i, s in enumerate(lines) if 'Climate Identifier' in s][0]
    search_header[6] = [i for i, s in enumerate(lines) if 'WMO Identifier' in s][0]
    search_header[7] = [i for i, s in enumerate(lines) if 'TC Identifier' in s][0]
    search_header[8] = [i for i, s in enumerate(lines) if 'Date/Time' in s][0]  # This is where the data actually starts

    # Does a bunch of stuff, but basically finds the right line, then cleans up the string
    station_meta = {
        'name': lines[search_header[0]].split(',')[1].replace('"', "").replace("\n", ""),
        'province': lines[search_header[1]].split(',')[1].replace('"', "").replace("\n", ""),
        'latitude': float(lines[search_header[2]].split(',')[1].replace('"', "").replace("\n", "")),
        'longitude': float(lines[search_header[3]].split(',')[1].replace('"', "").replace("\n", "")),
        'elevation': float(lines[search_header[4]].split(',')[1].replace('"', "").replace("\n", "")),
        'ID': lines[search_header[5]].split(',')[1].replace('"', "").replace("\n", ""),
        'WMO_ID': lines[search_header[6]].split(',')[1].replace('"', "").replace("\n", ""),
        'TC_ID': lines[search_header[7]].split(',')[1].replace('"', "").replace("\n", "")
    }

    data = pd.read_csv(file, header=search_header[8]-2)
    # Makes sure that the data starts on Jan 1st
    if data.values[0, 2] != 1 | data.values[0, 3] != 1:
        print('Data is not starting on January 1st. Make sure this is what you want!')

    return station_meta, data
