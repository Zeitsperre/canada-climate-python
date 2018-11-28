#!/bin/env python3

import os
from ftplib import FTP

import numpy as np
import pandas as pd
import requests


def main():
    # create new file structure from script directory
    output_dir = os.path.abspath("ec_station_output")
    os.makedirs(output_dir, exist_ok=True)

    # Connect and login
    ftp = FTP('ftp.tor.ec.gc.ca')
    ftp.login('client_climate')

    # Change working directory
    ftp.cwd('/Pub/Get_More_Data_Plus_de_donnees')

    # Download station inventory info
    filename = "Station Inventory EN.csv"
    ftp.retrbinary("RETR " + filename, open(os.path.join(output_dir, filename), 'wb').write)

    # import station inventory as pandas DataFrame
    stats = pd.read_csv(os.path.join(output_dir, filename), header=3)

    try:
        download_hourly(stats, output_dir)
        download_daily(stats, output_dir)
    except Exception as e:
        raise Exception(e)


def download_hourly(stats, outputdir):
    # get daily station data
    time_frame = '1'  # Corresponding code for hourly from readme info
    time_step = 'HLY'

    for d, _ in enumerate(stats['Name']):
        first_year = stats[time_step + ' First Year'][d]
        last_year = stats[time_step + ' Last Year'][d]

        # check that station has a first and last year value for DLY time step
        if not np.isnan(first_year) and not np.isnan(last_year):

            # remove special chars in name
            rep = {'\\': '_', '/': '_', ' ': '_'}
            name = stats['Name'][d]
            for old, new in rep.items():
                name = name.replace(old, new)

            # output variables
            province = '_'.join(stats["Province"][d].split())
            climate_id = stats['Climate ID'][d]
            station_id = stats['Station ID'][d]
            folder_id = '_'.join([climate_id, name])

            # make directory
            repo = os.path.join(outputdir, 'HLY', province, folder_id)
            os.makedirs(repo, exist_ok=True)

            for year in range(int(first_year), int(last_year + 1)):
                for month in range(1, 13):
                    base_url = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&' \
                               'stationID={0}&Year={1}&Month={2}&timeframe={3}&submit= Download+Data'
                    url = base_url.format(station_id, year, month, time_frame)
                    r = requests.get(url)
                    filename = '_'.join([climate_id, name, str(year), str(month).zfill(2), time_step])
                    outfile = os.path.join(repo, '.'.join([filename, 'csv']))

                    with open(outfile, 'wb') as f:
                        f.write(r.content)


def download_daily(stats, output_dir):
    # get daily station data
    time_frame = '2'  # Corresponding code for daily from readme info
    time_step = 'DLY'

    for d, _ in enumerate(stats['Name']):
        first_year = stats[time_step + ' First Year'][d]
        last_year = stats[time_step + ' Last Year'][d]

        # check that station has a first and last year value for DLY time step
        if not np.isnan(first_year) and not np.isnan(last_year):

            # remove special chars in name
            rep = {'\\': '_', '/': '_', ' ': '_'}
            name = stats['Name'][d]
            for old, new in rep.items():
                name = name.replace(old, new)

            # output variables
            province = '_'.join(stats["Province"][d].split())
            climate_id = stats['Climate ID'][d]
            station_id = stats['Station ID'][d]
            folder_id = '_'.join([climate_id, name])

            # make a directory
            repo = os.path.join(output_dir, 'DLY', province, folder_id)
            os.makedirs(repo, exist_ok=True)

            # loop through years and download
            for year in range(int(first_year), int(last_year + 1)):
                base_url = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&' \
                           'stationID={0}&Year={1}&Month={2}&timeframe={3}&submit= Download+Data'
                url = base_url.format(station_id, year, str(1), time_frame)
                r = requests.get(url)
                filename = '_'.join([climate_id, name, str(year), time_step])
                outfile = os.path.join(repo, '.'.join([filename, 'csv']))

                with open(outfile, 'wb') as f:
                    f.write(r.content)


if __name__ == '__main__':
    main()
