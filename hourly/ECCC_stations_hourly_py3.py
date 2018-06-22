#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert function developed by Richie Hindle
https://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str/1254499#1254499
"""

import codecs  # Needs to be removed. Obsolete.
import collections
import os
import sys
from datetime import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
import unicodecsv as csv


def convert(data):
    try:
        if isinstance(data, basestring):
            try:
                return str(data)
            except:
                return data.encode('ascii', 'ignore')
        elif isinstance(data, collections.Mapping):
            return dict(map(convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert, data))
        else:
            return data
    except UnicodeEncodeError:
        return ''


def period(dataframe):
    """
    Determines the earliest and latest date/times and returns the length
    of month in total number of days, accounting for leap years.
    """
    dates = np.array(dataframe['Date/Time'], dtype='datetime64[h]')
    min_date = np.datetime64(min(dates), dtype='datetime64[D]')
    max_date = np.datetime64(max(dates), dtype='datetime64[D]')
    month = dataframe['Month'][0]
    period = np.arange(min_date, max_date + 1, dtype='datetime64[D]')

    return month, period


def humid(dataframe):
    """
    Summarizes the indicators for Relative Humidity.
    """
    key = 'Rel Hum (%)'
    month, days = period(dataframe)

    humid_raw = dataframe[key]
    for count, factor in enumerate(humid_raw):  # Handling NoneTypes
        try:
            factor = float(factor)
        except (TypeError, ValueError):
            humid_raw[count] = 'NaN'

    humid_hourly = np.array(humid_raw, dtype=np.float)
    humid_hourly = np.ma.masked_where(np.isnan(humid_hourly), humid_hourly)

    if type(np.nansum(humid_hourly)) != np.float64:
        return False, key, month

    humid_daily = humid_hourly.reshape(len(humid_hourly) / 24, 24)
    min_humid = np.amin(humid_daily, axis=1)
    max_humid = np.amax(humid_daily, axis=1)

    y1 = min_humid
    y2 = max_humid
    hu_min, hu_max = y1.min(), y1.max()
    title = 'Relative Humidity'
    y1_label = '%'
    y2_label = None

    y1_title = 'Monthly Min Humidity: {0:.3}'.format(hu_min)
    y2_title = 'Monthly Max Humidity: {0:.3}'.format(hu_max)

    return days, y1, y2, month, title, y1_label, y2_label, y1_title, y2_title


def windchill(dataframe):
    """
    Summarizes the indicators for Wind Chill Factor.
    """
    key = 'Wind Chill'
    month, days = period(dataframe)

    wcf_raw = dataframe[key]
    for count, factor in enumerate(wcf_raw):  # Handling those annoying NoneTypes
        try:
            factor = float(factor)
        except (TypeError, ValueError):
            wcf_raw[count] = 'NaN'

    wcf_hourly = np.array(wcf_raw, dtype=np.float)
    wcf_hourly = np.ma.masked_where(np.isnan(wcf_hourly), wcf_hourly)

    if type(np.nansum(wcf_hourly)) != np.float64:
        return False, key, month

    wcf_daily = wcf_hourly.reshape(len(wcf_hourly) / 24, 24)
    min_wcf = np.amin(wcf_daily, axis=1)
    max_wcf = np.amax(wcf_daily, axis=1)

    y1 = min_wcf
    y2 = max_wcf
    minmean_wcf, maxmean_wcf = y1.mean(), y2.mean()
    title = 'Wind Chill Factor'
    y1_label = 'Deg C'
    y2_label = None

    y1_title = 'Avg Min Wind Chill: {0:.3} deg C'.format(minmean_wcf)
    y2_title = 'Avg Max Wind Chill: {0:.3} deg C'.format(maxmean_wcf)

    return days, y1, y2, month, title, y1_label, y2_label, y1_title, y2_title


def collect_that():
    """
    Collects all files starting with "eng-" and ending with ".csv"
    located in the same directory as the script. Need to consider
    making a method allowing for users to feed in a directory location
    if they want to scan a filesystem.
    """
    print
    'Scanning directories:\n'
    ec_stations = [ec for ec in os.listdir('.')
                   if ec.startswith('eng-hourly')]
    ec_stations.sort()

    if len(ec_stations) >= 1:
        return ec_stations
    else:
        raise Exception("No stations were collected. Verify CSV locations.")
        sys.exit()


def place_that(name):
    """
    When given a filename will dump station location headers
    to console and return a dictionary with raw unicode keys
    and values for station name and location variables.
    """
    try:
        location = str(name)
        with codecs.open(location, 'rb') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            verifier = csv.reader(f, dialect)
            for count, row in enumerate(verifier):  # Read and format metadata
                if count > 6:
                    break
            f.seek(0)
            names = ('Station Name'
                     , 'Province'
                     , 'Latitude'
                     , 'Longitude'
                     , 'Elevation'
                     , 'Climate Identifier'
                     , 'WMO Identifier'
                     , 'TC Identifier')
            datum = {}
            for name in names:
                datum[name] = []

            for count, row in enumerate(verifier):
                if count == 0:  # Special handling to deal with UTF-8 BOM
                    key = 'Station Name'
                    field = convert(row[1])
                    datum[key] = field
                    continue
                try:
                    if row[0] in names:
                        key = convert(row[0])
                        field = convert(row[1])
                        datum[key] = field
                except:
                    continue
        return datum
    except ValueError:
        raise Exception("Invalid station CSV. \
            Verify that CSVs hold Environment Canada station data.")
        pass


def grab_that(station):
    """
    A method that extracts climate data from CSV and converts it to a
    dictionary object.
    """
    with codecs.open(station, 'rb', ) as f:
        # Tries to figure out CSV formatting to address encoding issues.
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        lines = csv.reader(f, dialect)
        for i in range(16):  # Skips the metadata
            next(lines)

        names, datum = [], {}
        for column in lines:
            for name in column:
                names.append(name)
                datum[name] = []
            break

        reader = csv.DictReader(f, fieldnames=names, delimiter=',', quotechar='"')
        for row in reader:
            for column, value in row.iteritems():
                value = convert(value)
                datum.setdefault(column, []).append(value)
    return datum


def match_locations(locations):
    """
    A method to match locations that appear multiple times in the same list
    and return year-ordered lists that can then be plotted sequentially
    """

    ident = 'Climate Identifier'
    yr = 'Year'
    mon = 'Month'

    matches = []
    order_months = [[]]
    processed_stations = []
    try:
        for i, station1 in enumerate(locations):
            if (station1[ident], station1[yr][0]) in processed_stations:
                continue
            matches.append([])
            matches[-1].append(station1)
            order_months[-1].append(int(station1[mon][0]))
            for station2 in locations[i + 1:]:
                if station1[ident] == station2[ident] \
                        and int(station1[yr][0]) == int(station2[yr][0]) \
                        and int(station1[mon][0]) != int(station2[mon][0]):
                    matches[-1].append(station2)
                    order_months[-1].append(int(station2[mon][0]))
            processed_stations.append((station1[ident], station1[yr][0]))
        return matches
    except ValueError:
        raise Exception("Verify that CSV has valid dates and formatted properly")


def calc_that(match, plot):
    """
    A method that converts a unicode dictionary of climate data to ASCII and
    proceeds to calculate daily variables derived from it.
    """
    location = match.copy()

    # Depending on the plot type being calculated, only return the variables needed
    if plot == 0:
        return humid(location)
    elif plot == 1:
        return windchill(location)
    else:
        return "You need more plot styles"


def data_unpacker(matches, make_plots=True):
    """
    Unpacks the matches and match data to return continuous data
    that will be appended to CSVs. If make_plots == True, will create a
    series of subplots.
    """
    csv_list = []

    for match in matches:
        csv_meta = ('Station Name'
                    , 'Province'
                    , 'Latitude'
                    , 'Longitude'
                    , 'Elevation'
                    , 'Climate Identifier'
                    , 'WMO Identifier'
                    , 'TC Identifier')
        csv_data = {'Date': [], 'Min Rel Humid (%)': [], 'Max Rel Humid (%)': [],
                    'Min WCF (deg C)': [], 'Max WCF (deg C)': []}
        for keys in csv_meta:
            csv_meta = {keys: match[0][keys]}
            csv_data.update(csv_meta)
        if len(match) > 1:
            print
            '\nMulti-Month Set Found; Matched as follows:'
            for iterable, station in enumerate(match):
                print(station['Station Name'] + ' ID:' + station['Climate Identifier']
                      + ' for Month ' + station['Month'][0] + ' in ' + station['Year'][0])

            # Begin subplotting processes
            for plot in range(2):
                if make_plots:
                    f, axarr = plt.subplots(len(match), 1, sharex=True)
                for subplot, station in enumerate(match):
                    analysis = calc_that(station, plot)

                    if make_plots:
                        plot_maker(analysis, axarr, subplot, plot)

                    length = len(period(station)[1])
                    empty = np.ma.masked_array(np.zeros((length,)), mask=np.ones((length,)))

                    # Grab formatted data as it is iterated over
                    if plot == 0:
                        csv_data['Date'].extend(period(station)[1])
                        if analysis[0] is False:
                            csv_data['Min Rel Humid (%)'].extend(empty)
                            csv_data['Max Rel Humid (%)'].extend(empty)
                        else:
                            csv_data['Min Rel Humid (%)'].extend(analysis[1])
                            csv_data['Max Rel Humid (%)'].extend(analysis[2])
                    if plot == 1:
                        if analysis[0] is False:
                            csv_data['Min WCF (deg C)'].extend(empty)
                            csv_data['Max WCF (deg C)'].extend(empty)
                        else:
                            csv_data['Min WCF (deg C)'].extend(analysis[1])
                            csv_data['Max WCF (deg C)'].extend(analysis[2])

                if make_plots:
                    f.subplots_adjust(hspace=0.5)
                    f.text(0.5, 0.04, 'Day in Month', ha='center', va='center')
                    stationplace = match[0]['Station Name'] + ' Station for Year ' + match[0]['Year'][0]
                    f.text(0.5, 0.96, stationplace, ha='center', va='center')

        elif len(match) == 1:
            print
            '\nSingle Month Station Found:'
            print(match[0]['Station Name'] + ' ID:' + match[0]['Climate Identifier']
                  + ' for Month ' + match[0]['Month'][0] + ' in ' + match[0]['Year'][0])

            # Begin plotting processes
            if make_plots:
                f, axarr = plt.subplots(3, 1, sharex=True)
            for plot in range(2):
                analysis = calc_that(match[0], plot)

                if make_plots:
                    plot_maker(analysis, axarr, plot, plot)

                length = len(period(match[0])[1])
                empty = np.ma.masked_array(np.zeros((length,)), mask=np.ones((length,)))

                # Grab formatted data as it is iterated over
                if plot == 0:
                    csv_data['Date'].extend(period(match[0])[1])
                    if analysis[0] is False:
                        csv_data['Min Rel Humid (%)'].extend(empty)
                        csv_data['Max Rel Humid (%)'].extend(empty)
                    else:
                        csv_data['Min Rel Humid (%)'].extend(analysis[1])
                        csv_data['Max Rel Humid (%)'].extend(analysis[2])
                if plot == 1:
                    if analysis[0] is False:
                        csv_data['Min WCF (deg C)'].extend(empty)
                        csv_data['Max WCF (deg C)'].extend(empty)
                    else:
                        csv_data['Min WCF (deg C)'].extend(analysis[1])
                        csv_data['Max WCF (deg C)'].extend(analysis[2])

            if make_plots:
                f.subplots_adjust(hspace=0.25)
                f.text(0.5, 0.04, 'Day in Month', ha='center', va='center')
                stationplace = match[0]['Station Name'] + ' Station for Year ' + match[0]['Year'][0]
                f.text(0.5, 0.96, stationplace, ha='center', va='center')

        else:
            print
            "This should never happen."
        csv_list.append(csv_data)
        if make_plots:
            plt.show()
    return csv_list


def plot_maker(analysis, axarr, subplot, plot):
    """
    Using plot names, axes, year and titles, creates a sublot or twin subplot.
    Is looped over to create subplots with multi-year or multi-station data.
    """
    # Import the values derived from calc_that or skip the month
    try:
        days, y1, y2, month, title, y1_label, y2_label, y1_title, y2_title = analysis
    except (TypeError, ValueError):
        print
        analysis[1] + " for Month " + analysis[2] + " is being skipped"
        return

    # General plot elements
    x = np.arange(1, len(days) + 1)
    title = title + ' in Month ' + month
    axarr[subplot].set_title(title)
    axarr[subplot].set_xlim(min(x), max(x))
    axarr[subplot].grid(True)

    try:
        if plot == 0:  # Create the Relative Humidity plot
            c1 = 'gold'
            c2 = 'mediumslateblue'
            axarr[subplot].tick_params('y')
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, '-o', color=c1)
            axarr[subplot].plot(x, y2, '-o', color=c2)
            axarr[subplot].legend()
            bottom = y1.min()
            axarr[subplot].text(5, bottom + 15, y1_title)
            axarr[subplot].text(5, bottom + 40, y2_title)

        elif plot == 1:  # Create the Wind Chill Factor plot
            c1 = 'limegreen'
            c2 = 'darkviolet'
            axarr[subplot].tick_params('y')
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, '-o', color=c1)
            axarr[subplot].plot(x, y2, '-o', color=c2)
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].text(5, -5, y1_title)
            axarr[subplot].text(15, -5, y2_title)

        else:
            return "You need more plot styles."
        return
    except TypeError:
        raise Exception("That didn\'t work.")


def make_csvs(csv_list):
    """
    Writes out CSV with two headers detailing the station metadata and the
    variables being written out. If a file for an existing station exists,
    subsequent years will be appended to the file.
    """
    now = dt.now()

    head = ('Station Name'
            , 'Province'
            , 'Latitude'
            , 'Longitude'
            , 'Elevation'
            , 'Climate Identifier'
            , 'WMO Identifier'
            , 'TC Identifier')
    body = ('Date', 'Min Rel Humid (%)', 'Max Rel Humid (%)'
            , 'Min WCF (deg C)', 'Max WCF (deg C)')

    for csv_station in csv_list:
        ident = csv_station['Climate Identifier']
        name = str(ident) + '_humid_wcf.' + now.strftime("%Y-%m-%d") + '.csv'
        body = ('Date'
                , 'Min Rel Humid (%)'
                , 'Max Rel Humid (%)'
                , 'Min WCF (deg C)'
                , 'Max WCF (deg C)')

        if name in os.listdir('.'):
            with codecs.open(name, 'a') as f:
                list_writer = csv.writer(f, delimiter=',')
                list_writer.writerows(zip(*[csv_station[key] for key in body]))
        else:
            with codecs.open(name, 'wb') as f:
                dict_writer = csv.DictWriter(f, head, extrasaction='ignore')
                dict_writer.writeheader()
                dict_writer.writerow(csv_station)
            with codecs.open(name, 'a') as f:
                dict_writer = csv.DictWriter(f, body, extrasaction='ignore')
                dict_writer.writeheader()
            with codecs.open(name, 'a') as f:
                list_writer = csv.writer(f, delimiter=',')
                list_writer.writerows(zip(*[csv_station[key] for key in body]))


def hourly_stations(make_plots):
    """
    The main script that calls other methods; Odd calls and methods that are
    yet to be integrated are placed here to ensure script methods can be run to
    completion before they are used by other scripts.
    """
    fnames = collect_that()

    locations = []
    if len(fnames) > 1:
        for f in fnames:
            place = place_that(f)
            locations.append(place)
        print
        len(fnames), "station readings gathered"
    else:
        place = place_that(fnames[0])
        locations.append(place)
        print
        "Single station reading gathered"

    for count, station in enumerate(fnames):
        datum = grab_that(station)
        locations[count].update(datum)

    matches = match_locations(locations)
    csv_list = data_unpacker(matches, make_plots)
    make_csvs(csv_list)

    print
    'Done!'
    return 0


if __name__ == "__main__":
    """
    For debugging purposes.
    """
    make_plots = False
    plots = raw_input("Do you want to produce plots of data? y/[n]")
    if plots in ('y', 'Y'):
        make_plots = True
    print
    "Making Plots!" * make_plots

    hourly_stations(make_plots)
