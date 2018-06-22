import glob
from ftplib import FTP

import numpy as np
import pandas
import requests


def main():
    OutDir = r'W:\Projets\EC_stations_download\\'
    if not glob.os.path.exists(OutDir):
        glob.os.makedirs(OutDir)

    # Connect and login
    ftp = FTP('ftp.tor.ec.gc.ca')
    ftp.login('client_climate')
    # Change working directory
    ftp.cwd('/Pub/Get_More_Data_Plus_de_donnees')

    # Download station inventory info
    filename = 'Station Inventory EN.csv'
    ftp.retrbinary("RETR " + filename, open(OutDir + filename, 'wb').write)

    # import station inventory as pandas dataframe
    stats = pandas.read_csv(OutDir + filename, header=3)

    download_daily(stats, OutDir)
    download_hourly(stats, OutDir)


def download_hourly(stats, OutDir):
    # get daily station data
    time_step = 'HLY'
    timeframe = 'timeframe=1'  # Corresponding code for hourly from readme info
    stats = stats[
        stats[time_step + ' First Year'].notnull()]  # stats[:][~np.isnan(stats[time_step +' First Year' ])] #get data
    stats = stats[stats[time_step + ' Last Year'].notnull()]  # stats[:][~np.isnan(stats[time_step +' Last Year' ])]

    for index, row in stats.iterrows():
        # Only get eastern provinces for now
        if 'QUEBEC' in row['Province']:  # \
            # or 'ONTARIO' in row['Province']\
            # or 'NOVA SCOTIA' in row['Province']\
            # or 'PRINCE EDWARD ISLAND' in row['Province']\
            # or 'ONTARIO' in row['Province']\
            # or 'NEWFOUNDLAND' in row['Province']\
            # or 'NEW BRUNSWICK' in row['Province']\
            # or 'MANITOBA' in row['Province']:
            # check that station has a first and last year value for HLY time step
            if not np.isnan(row[time_step + ' First Year']) and not np.isnan(row[time_step + ' Last Year']):
                # output directory name
                print(row['Name'])
                outrep1 = OutDir + time_step + '\\' + row['Province'].replace(' ', '_') + '\\' + row[
                    'Climate ID'] + '_' + row['Name'].replace('\\', '_').replace('/', '_').replace(' ', '_')
                # create if necessary
                if not glob.os.path.exists(outrep1):
                    glob.os.makedirs(outrep1)
                # loop through years and download
                for y in range(int(row[time_step + ' First Year']), int(row[time_step + ' Last Year'] + 1)):
                    for m in range(1, 13):
                        URL = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=' + str(
                            row['Station ID']) + '&Year=' + str(y) + '&Month=' + str(
                            m) + '&' + timeframe + '&submit= Download+Data'
                        r = requests.get(URL)
                        outfile = outrep1 + '\\' + row['Climate ID'] + '_' + row['Name'].replace('\\', '_').replace('/',
                                                                                                                    '_').replace(
                            ' ', '_') + '_' + str(y) + '_' + str(m).zfill(2) + '_' + time_step + '.csv'

                        with open(outfile, 'wb') as f:
                            f.write(r.content)


def download_daily(stats, OutDir):
    # get daily station data
    time_step = 'DLY'
    timeframe = 'timeframe=2'  # Corresponding code for daily from readme info
    for d in range(0, len(stats['Name'])):

        # check that station has a first and last year value for DLY time step
        if not np.isnan(stats[time_step + ' First Year'][d]) and not np.isnan(stats[time_step + ' Last Year'][d]):
            # output directory name
            outrep1 = OutDir + time_step + '\\' + stats['Province'][d].replace(' ', '_') + '\\' + stats['Climate ID'][
                d] + '_' + stats['Name'][d].replace('\\', '_').replace('/', '_').replace(' ', '_')
            # create if necessary
            if not glob.os.path.exists(outrep1):
                glob.os.makedirs(outrep1)
            # loop through years and download
            for y in range(int(stats[time_step + ' First Year'][d]), int(stats[time_step + ' Last Year'][d] + 1)):
                URL = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=' + str(
                    stats['Station ID'][d]) + '&Year=' + str(y) + '&' + timeframe + '&submit= Download+Data'
                r = requests.get(URL)
                outfile = outrep1 + '\\' + stats['Climate ID'][d] + '_' + stats['Name'][d].replace('\\', '_').replace(
                    '/', '_').replace(' ', '_') + '_' + str(y) + '_' + time_step + '.csv'

                with open(outfile, 'wb') as f:
                    f.write(r.content)


if __name__ == '__main__':
    main()
