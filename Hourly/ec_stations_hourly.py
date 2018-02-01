#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 10:05:19 2018
@author: trevor

To determine the daily station statistics (unused)
        #bin_size = 24 
        #bin_layout = np.arange(humid.size)//bin_size
        #avg_humid = np.bincount(bin_layout,humid)/np.bincount(bin_layout)
"""
import os
import sys
import codecs
import unicodecsv as csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as dates
import numpy as np
from pdb import set_trace as stop


def period(dataframe):
    """
    Determines the earliest and latest dates and returns the length 
    of month in total number of days, accounting for leap years.
    """
    min_date = np.datetime64(min(dataframe['Date/Time']))
    max_date = np.datetime64(max(dataframe['Date/Time']))
    month = (dataframe['Month'][0])
    period = np.arange(min_date, max_date + np.timedelta64(1,'D') , dtype='datetime64[D]')
    
    return month, period


def humid(dataframe):
    """
    Formats the indicators for Relative Humidity.
    """
    month, days = period(dataframe)

    humid_hourly = np.array(dataframe['Rel Hum (%)'], dtype = np.float)
    humid_hourly = np.ma.masked_where(np.isnan(humid_hourly), humid_hourly)
    
    humid_daily = humid_hourly.reshape(len(humid_hourly)/24, 24)
    min_humid = np.amin(humid_daily, axis = 1)
    max_humid = np.amax(humid_daily, axis = 1)

    # TRY CATCHING EMPTY ARRAYS RIGHT HERE

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
    month, days = period(dataframe)

    wcf_raw = dataframe['Wind Chill']
    for count, factor in enumerate(wcf_raw): #Handling those annoying NoneTypes
        try:
            factor = float(factor)
        except (TypeError, ValueError): 
            wcf_raw[count] = 'NaN'
            
    wcf_hourly = np.array(wcf_raw, dtype = np.float)
    wcf_hourly = np.ma.masked_where(np.isnan(wcf_hourly), wcf_hourly)

    wcf_daily = wcf_hourly.reshape(len(wcf_hourly)/24, 24)
    min_wcf = np.amin(wcf_daily, axis = 1)
    max_wcf = np.amax(wcf_daily, axis = 1)   
    
    # TRY CATCHING EMPTY ARRAYS RIGHT HERE
    
    y1 = min_wcf
    y2 = max_wcf
    minmean_wcf, maxmean_wcf = y1.mean(), y2.mean()
    title = 'Wind Chill Factor'
    y1_label = 'Deg C'
    y2_label = None
    
    y1_title = 'Average Min Wind Chill: {0:.3} degrees'.format(minmean_wcf)
    y2_title = 'Average Max Wind Chill: {0:.3} degrees'.format(maxmean_wcf)

    return days, y1, y2, month, title, y1_label, y2_label, y1_title, y2_title


def collect_that():
    """
    Collects all files starting with "eng-" and ending with ".csv"  
    located in the same directory as the script. Need to consider 
    making a method allowing for users to feed in a directory location 
    if they want to scan a filesystem.
    """
    print 'Scanning directories:\n'
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
            for count, row in enumerate(verifier): # Read and format metadata 
                print ': '.join(row)
                if count > 6:
                    print '\n'
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
                if count == 0: # Special handling to deal with UTF-8 BOM
                    key = 'Station Name'
                    field = row[1]
                    datum[key] = field
                    continue
                try:
                    if row[0] in names:
                        key = row[0]
                        field = row[1]
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
        #Tries to figure out CSV formatting to address encoding issues.
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        lines = csv.reader(f, dialect)
        for i in range(16): # Skips the metadata
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
                value = value
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
            if (station1[ident],station1[yr][0]) in processed_stations:
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
            processed_stations.append((station1[ident],station1[yr][0]))
        return matches
    except ValueError:
        raise Exception("Verify that CSV has valid dates and formatted properly")

def calc_that(match, plot):
    """
    A method that converts a unicode dictionary of climate data to ASCII and 
    proceeds to calculate daily variables derived from it.
    """
    location = match.copy()

    for key in location:
        newkey = key.encode('ascii', 'ignore')
        location[newkey] = location.pop(key)
        for count, val in enumerate(location[newkey]):
            try:
                newval = val.encode('ascii', 'ignore')
                location[newkey][count] = newval
            except TypeError:
                continue
            except AttributeError:
                continue
        
    # Depending on the plot type being calculated, only return the variables needed
    if plot == 0:    
        return humid(location)
    elif plot == 1:
        return windchill(location)
    else:
        return 'Gonna need more than that'


def plot_maker(analysis, axarr, subplot, plot):
    """
    Using plot names, axes, year and titles, creates a sublot or twin subplot.
    Is looped over to create subplots with multi-year or multi-station data.
    """
    # Import the values derived from calc_that
    try:
        days, y1, y2, month, title, y1_label, y2_label, y1_title, y2_title = analysis
    except (TypeError, ValueError):
        try:
            # Final check for empty arrays
            print analysis[0] + "for Month" + analysis[1] + "is being skipped"
        except:
            print "Unskippable Error. Abandon Ship!"
            return
    
    # General plot elements
    x = np.arange(1, len(days)+1)
    title = title + ' in Month ' + month
    axarr[subplot].set_title(title)
    axarr[subplot].set_xlim(min(x), max(x))
    axarr[subplot].grid(True)

    try:
        if plot == 0: # Create the Relative Humidity plot
            c1 = 'gold'
            c2 = 'mediumslateblue'
            axarr[subplot].tick_params('y')
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, '-', color = c1)
            axarr[subplot].plot(x, y2, '-', color = c2)
            axarr[subplot].legend()
            bottom = y1.min()
            axarr[subplot].text(5, bottom+15, y1_title)
            axarr[subplot].text(5, bottom+40, y2_title)

        elif plot == 1: # Create the Wind Chill Factor plot
            c1 = 'limegreen'
            c2 = 'darkviolet'
            axarr[subplot].tick_params('y')
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, '-', color = c1)
            axarr[subplot].plot(x, y2, '-', color = c2)
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].text(5, -5, y1_title)
            axarr[subplot].text(15, -5, y2_title)

        else:
            return 'You need more plot styles.'            
        return
    except TypeError:
        raise Exception("That didn\'t work.")

def data_unpacker(matches):
    """
    Unpacks the matches and match data to call plotting functions and returns
    continuous data for specific fields to be appended to CSVs
    """
#    csv_list = [[]]
#    csv_data = {'Date':[], 'Min Rel Humid (%)':[], 'Max Rel Humid (%)':[], 'Min WCF (deg C)':[], 'Max WCF (deg C)':[]}
#    csv_meta = names = ('Station Name'
#                     , 'Province'
#                     , 'Latitude'
#                     , 'Longitude'
#                     , 'Elevation'
#                     , 'Climate Identifier'
#                     , 'WMO Identifier'
#                     , 'TC Identifier')

    for match in matches:
        if len(match) > 1:
            print '\nMulti-Month Set Found; Matched as follows:'
            for iterable, station in enumerate(match):
                print (station['Station Name'] + ' ID:' + station['Climate Identifier'] 
                    + ' for Month ' + station['Month'][0] + ' in ' + station['Year'][0])
#                if humid(station) is None or windchill(station) is None:
#                    csv_data['Date'].extend(period(station))
#                    csv_data['Min Rel Humid (%)'].extend(np.empty(len(period(station))))
#                    csv_data['Max Rel Humid (%)'].extend(np.empty(len(period(station))))
#                    csv_data['Min WCF (deg C)'].extend(np.empty(len(period(station))))
#                    csv_data['Max WCF (deg C)'].extend(np.empty(len(period(station))))
#                    del match[iterable]
                
                #stop()
            # Begin subplotting processes   
            for plot in range(2):
                f, axarr = plt.subplots(len(match), 1, sharex = True)
                for subplot, station in enumerate(match):

                    analysis = calc_that(station, plot)
                    plot_maker(analysis, axarr, subplot, plot)
                    
#                    # Grabbing metadata
#                    if plot == 0:
#                        if subplot == 0:
#                            for keys in csv_meta:                                                                    
#                                csv_meta = {keys:station[keys]}
#                                csv_data.update(csv_meta)
#                        
#                        # Grab formatted data as it is iterated over                  
#                        csv_data['Date'].extend(analysis[0])
#                        csv_data['Min Rel Humid (%)'].extend(analysis[1])
#                        csv_data['Max Rel Humid (%)'].extend(analysis[2])
#                    if plot == 1:
#                        csv_data['Min WCF (deg C)'].extend(analysis[1])
#                        csv_data['Max WCF (deg C)'].extend(analysis[2])
                
                f.subplots_adjust(hspace=0.5)
                f.text(0.5, 0.04, 'Day in Month', ha = 'center', va = 'center')
                stationplace = match[0]['Station Name'] + ' Station for Year ' + match[0]['Year'][0]
                f.text(0.5, 0.96, stationplace, ha = 'center', va = 'center')
 
        elif len(match) == 1:
            print '\nSingle Month Station Found:'
            print (match[0]['Station Name'] + ' ID:' + match[0]['Climate Identifier']
                + ' for Month ' + station['Month'][0] + ' in ' + match[0]['Year'][0])

            # Begin plotting processes
            f, axarr = plt.subplots(3, 1, sharex = True)
            for subplot in range(2):
                analysis = calc_that(match[0], subplot)
                plot_maker(analysis, axarr, subplot, subplot)
                
                # Grabbing metadata
                if plot == 0:
                    if station == 0:
                        pass
#                        for keys in csv_meta.keys():                                                                    
#                            csv_meta[keys] = station[keys]
                        
                    # Grab formatted data as it is iterated over                     
#                    csv_data['Date'].extend(analysis[0])
#                    csv_data['Min Rel Humid (%)'].extend(analysis[1])
#                    csv_data['Max Rel Humid (%)'].extend(analysis[2])
#                if plot == 1:
#                    csv_data['Min WCF (deg C)'].extend(analysis[1])
#                    csv_data['Max WCF (deg C)'].extend(analysis[2])
            
            f.subplots_adjust(hspace=0.25)
            f.text(0.5, 0.04, 'Day in Month', ha = 'center', va = 'center')
            stationplace = match[0]['Station Name'] + ' Station for Year ' + match[0]['Year'][0]
            f.text(0.5, 0.96, stationplace, ha = 'center', va = 'center')
        else:
            print 'This should never happen.'
        plt.show()

    return #csv_data

def daily_stations():
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
        print len(fnames), 'station readings gathered'
    else:
        place = place_that(fnames[0])
        locations.append(place)
        print 'Single station reading gathered'

    for count, station in enumerate(fnames):
        datum = grab_that(station)
        locations[count].update(datum)

    matches = match_locations(locations)
 
    csv_data = data_unpacker(matches)

    return csv_data
    
if __name__ == "__main__":
    '''
    For debugging purposes.
    '''
    daily_stations()
