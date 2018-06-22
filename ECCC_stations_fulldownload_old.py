import os
from ftplib import FTP

import numpy as np
import pandas as pd
import requests


def main():
    # create new file structure from script directory
    outputdir = os.path.abspath("ec_station_output")
    os.makedirs(outputdir, exist_ok=True)

    # Connect and login
    ftp = FTP('ftp.tor.ec.gc.ca')
    ftp.login('client_climate')

    # Change working directory
    ftp.cwd('/Pub/Get_More_Data_Plus_de_donnees')

    # Download station inventory info
    fname = "Station Inventory EN.csv"
    ftp.retrbinary("RETR " + fname, open(os.path.join(outputdir, fname), 'wb').write)

    # import station inventory as pandas dataframe
    stats = pd.read_csv(os.path.join(outputdir, fname), header=3)

    download_hourly(stats, outputdir)
    download_daily(stats, outputdir)


def download_hourly(stats, outputdir):
    # get daily station data
    tframe = '1'  # Corresponding code for hourly from readme info
    tstep = 'HLY'

    for d, _ in enumerate(stats['Name']):
        firstyear = stats[tstep + ' First Year'][d]
        lastyear = stats[tstep + ' Last Year'][d]

        # check that station has a first and last year value for DLY time step
        if not np.isnan(firstyear) and not np.isnan(lastyear):

            # remove special chars in name
            rep = {'\\': '_', '/': '_', ' ': '_'}
            name = stats['Name'][d]
            for old, new in rep.items():
                name = name.replace(old, new)

            # output variables
            province = '_'.join(stats["Province"][d].split())
            climateid = stats['Climate ID'][d]
            stationid = stats['Station ID'][d]
            folderid = '_'.join([climateid, name])

            # make directory
            repo = os.path.join(outputdir, 'HLY', province, folderid)
            os.makedirs(repo, exist_ok=True)

            for yyyy in range(int(firstyear), int(lastyear + 1)):
                for mm in range(1, 13):
                    baseurl = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&' \
                              'stationID={0}&Year={1}&Month={2}&timeframe={3}&submit= Download+Data'
                    url = baseurl.format(stationid, yyyy, mm, tframe)
                    r = requests.get(url)
                    fname = '_'.join([climateid, name, str(yyyy), str(mm).zfill(2), tstep])
                    outfile = os.path.join(repo, '.'.join([fname, 'csv']))

                    with open(outfile, 'wb') as f:
                        f.write(r.content)


def download_daily(stats, outputdir):
    # get daily station data
    tframe = '2'  # Corresponding code for daily from readme info
    tstep = 'DLY'

    for d, _ in enumerate(stats['Name']):
        firstyear = stats[tstep + ' First Year'][d]
        lastyear = stats[tstep + ' Last Year'][d]

        # check that station has a first and last year value for DLY time step
        if not np.isnan(firstyear) and not np.isnan(lastyear):

            # remove special chars in name
            rep = {'\\': '_', '/': '_', ' ': '_'}
            name = stats['Name'][d]
            for old, new in rep.items():
                name = name.replace(old, new)

            # output variables
            province = '_'.join(stats["Province"][d].split())
            climateid = stats['Climate ID'][d]
            stationid = stats['Station ID'][d]
            folderid = '_'.join([climateid, name])

            # make a directory
            repo = os.path.join(outputdir, 'DLY', province, folderid)
            os.makedirs(repo, exist_ok=True)

            # loop through years and download
            for yyyy in range(int(firstyear), int(lastyear + 1)):
                baseurl = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&' \
                          'stationID={0}&Year={1}&Month={2}&timeframe={3}&submit= Download+Data'
                url = baseurl.format(stationid, yyyy, str(1), tframe)
                r = requests.get(url)
                fname = '_'.join([climateid, name, str(yyyy), tstep])
                outfile = os.path.join(repo, '.'.join([fname, 'csv']))

                with open(outfile, 'wb') as f:
                    f.write(r.content)


if __name__ == '__main__':
    main()
