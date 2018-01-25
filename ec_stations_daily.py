#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 10:05:19 2018
@author: trevor
"""
import os
import sys
import codecs
import unicodecsv as csv
import matplotlib.pyplot as plt
#import scipy.optimize as sc
import numpy as np
import pdb


def collect_that():
    """
    Collects all files starting with "eng-" and ending with ".csv"  
    located in the same directory as the script. Need to consider 
    making a method allowing for users to feed in a directory location 
    if they want to scan a filesystem.
    """
    print 'Scanning directories:\n'
    ec_stations = [ec for ec in os.listdir('.')
                   if ec.startswith('eng-')]
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
        raise Exception("Not a valid station CSV. \
            Verify that CSV holds Environment Canada station data.")


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
        for i in range(25): # Skips the metadata
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
    year = 'Year'

    matches = []
    order_years = [[]]
    processed_stations = []
    try:
        for i, station1 in enumerate(locations):
            if station1[ident] in processed_stations:
                continue
            matches.append([])
            matches[-1].append(station1)
            order_years[-1].append(int(station1[year][0]))
            for station2 in locations[i + 1:]:
                if station1[ident] == station2[ident] \
                        and int(station1[year][0]) != int(station2[year][0]):
                    matches[-1].append(station2)
                    order_years[-1].append(int(station2[year][0]))
            processed_stations.append(station1[ident])
            matches[-1] = [x for _, x in sorted(zip(order_years[-1], matches[-1]))]
    
        return matches
    except ValueError:
        raise Exception("Verify that CSV has valid dates and formatted properly")

def calc_that(match, plot):
    """
    A method that converts a unicode dictionary of 
    climate data to ASCII and proceeds to create a dataframe 
    derived from it.
    """
    location = match
    for key in match:
        newkey = key.encode('ascii', 'ignore')
        location[newkey] = location.pop(key)
        for count, val in enumerate(match[newkey]):
            try:
                newval = val.encode('ascii', 'ignore')
                location[newkey][count] = newval
            except TypeError:
                continue

    def out_period(dataframe):
        """
        Determines the earliest and latest dates and returns the lenth of year.
        Needed for leap-year handling.
        """
        min_date = np.datetime64(min(dataframe['Date/Time']))
        max_date = np.datetime64(max(dataframe['Date/Time']))
        year = (dataframe['Year'][0])
        period = np.arange(min_date+1, max_date+2)
        return year, period

    def out_temp(dataframe):
        """
        Formats the min and max temperature series and creates labels
        """
        year, period = out_period(dataframe)

        max_temp_raw = np.array(dataframe['Max Temp (C)'])
        max_temp_masked = np.ma.masked_where(max_temp_raw == '', max_temp_raw)
        max_temp = np.array([float(val) for val in max_temp_masked])

        min_temp_raw = np.array(dataframe['Min Temp (C)'])
        min_temp_masked = np.ma.masked_where(min_temp_raw == '', min_temp_raw)
        min_temp = np.array([float(val) for val in min_temp_masked])

        x = np.arange(0., len(period))
        y1 = min_temp
        y2 = max_temp
        emint, emaxt = min(y1), max(y2)
        title = 'Temperature'
        y1_label = 'Degrees Celsius'
        y2_label = None
        y1_title = 'Extreme Min Temp: {}'.format(emint)
        y2_title = 'Extreme Max Temp: {}'.format(emaxt)

        return x, y1, y2, year, title, y1_label, y2_label, y1_title, y2_title

    def out_precip(dataframe):
        """
        Calculates and formats value indicators for precipitation and snow.
        """
        year, period = out_period(dataframe)

        tot_ppt_raw = np.array(dataframe['Total Precip (mm)'])
        tot_ppt_masked = np.ma.masked_where(tot_ppt_raw == '', tot_ppt_raw)
        tot_precip = np.array([float(val) for val in tot_ppt_masked])

        snow_raw = np.array(dataframe['Snow on Grnd (cm)'])
        snow_masked = np.ma.masked_where(snow_raw == '', snow_raw)
        snow = np.array([float(val) for val in snow_masked])

        x = np.arange(0., len(period))
        y1 = snow
        y2 = tot_precip
        sum_ppt, max_snow = np.nansum(y1), max(y2)
        title = 'Precipitation and Snow on Ground'
        y1_label = 'Snow on Ground (cm)'
        y2_label = 'Precipitation (mm)'
        y1_title = 'Day with Most Snow on Ground: {} cm'.format(max_snow)
        y2_title = 'Total Annual Precipitation: {} mm'.format(sum_ppt)

        return x, y1, y2, year, title, y1_label, y2_label, y1_title, y2_title

    def out_dd10(dataframe):
        """
        Calculates and formats value indicators for degree-days
        with base 10 Celsius.
        """
        def degree_days(low, high):
            #This may need to be revised to constrict dates to growing season.
            dd = (((low + high) - 10) / 2)
            if dd < 0:
                dd = 0
            return dd

        year, period = out_period(dataframe)

        max_temp_raw = np.array(dataframe['Max Temp (C)'])
        max_temp_masked = np.ma.masked_where(max_temp_raw == '', max_temp_raw)
        max_temp = np.array([float(val) for val in max_temp_masked])

        min_temp_raw = np.array(dataframe['Min Temp (C)'])
        min_temp_masked = np.ma.masked_where(min_temp_raw == '', min_temp_raw)
        min_temp = np.array([float(val) for val in min_temp_masked])

        x = np.arange(0., len(period))
        y1 = map(degree_days, min_temp, max_temp)
        y2 = None
        max_daily, sum_daily = max(y1), np.nansum(y1)
        title = 'Degree-Days Above 10 Celsius'
        y1_label = 'DD > 10 Celsius'
        y2_label = None
        y1_title = 'Maximum Daily Value: {}'.format(max_daily)
        y2_title = 'Sum of Daily Values: {}'.format(sum_daily)

        return x, y1, y2, year, title, y1_label, y2_label, y1_title, y2_title

    # Depending on the plot type being calculated, only return the variables needed
    if plot == 0:
        temp = out_temp(location) 
        return temp
    elif plot == 1:
        precip = out_precip(location)
        return precip
    elif plot == 2:
        dd10 = out_dd10(location)
        return dd10
    else:
        return 'Gonna need more than that'


def plot_maker(analysis, axarr, subplot, plot):
    """
    Using plot names, axes, year and titles, creates a sublot or twin subplot.
    Is looped over to create subplots with multi-year or multi-station data.
    """
    # Import the values derived from calc_that
    x, y1, y2, year, title, y1_label, y2_label, y1_title, y2_title = analysis
        
    # General plot elements
    title = title + ' in ' + year
    axarr[subplot].set_title(title)
    axarr[subplot].set_xlim(min(x), max(x))
    axarr[subplot].grid(True)
        
    try:
        if plot == 0: # Create the Min and Max Temperature plot
            c1 = 'cornflowerblue'
            c2 = 'firebrick'
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, 'o', color = c1)
            axarr[subplot].plot(x, y2, 'o', color = c2)
            axarr[subplot].legend()

            axarr[subplot].text(160, -20, y1_title)
            axarr[subplot].text(160, -10, y2_title)

        elif plot == 1: # Create the Snow and Precipitation plot
            # The axes are not correct in this figure. Need to be flipped.
            c1 = 'black'
            c2 = 'royalblue'
            axarr[subplot].tick_params('y', colors = c1)
            axarr[subplot].bar(x, y1, color = c1, edgecolor = c1)
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].tick_params('y', colors = c1)
            
            axarr[subplot].text(160, 25, y1_title)
            axarr[subplot].text(160, 15, y2_title)
            
            axalt = axarr[subplot].twinx()
            axalt.plot(x, y2, 'o', color = c2)
            axalt.set_ylabel(y2_label)
            axalt.tick_params('y', colors = c2)
        
        elif plot == 2: # Create the Degree-Days plot
            c1 = 'forestgreen'
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, '-', color = c1)
            axarr[subplot].text(10, 16, y1_title)
            axarr[subplot].text(10, 12, y2_title)
       
        else:
            return 'You need more plot styles.'
            
        return None

    except TypeError:
        raise Exception("That didn\'t work.")


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
        print len(fnames), 'stations gathered'
    else:
        place = place_that(fnames[0])
        locations.append(place)
        print 'Single station gathered'

    for count, station in enumerate(fnames):
        datum = grab_that(station)
        locations[count].update(datum)

    matches = match_locations(locations)
    
    #Consider cleaning this up and turning this into its own function.    
    for match in matches:
        if len(match) > 1:
            print '\nMulti-Year Set Found; Matched as follows:'
            for station in match:
                print station['Station Name'] + ' ID ' + station['Climate Identifier'] + ' in ' + station['Year'][0]   
            for plot in range(3):
                f, axarr = plt.subplots(len(match), 1, sharex = True)
                for subplot, station in enumerate(match):
                    analysis = calc_that(station, plot)
                    plot_maker(analysis, axarr, subplot, plot)
                
                f.subplots_adjust(hspace=0.25)
                f.text(0.5, 0.04, 'Day of Year', ha = 'center', va = 'center')
                stationplace = match[0]['Station Name'] + ' Station'
                f.text(0.5, 0.96, stationplace, ha = 'center', va = 'center')
        
        elif len(match) == 1:
            print '\nSingle Year Station Found:'
            print match[0]['Station Name'] + ' ID ' + match[0]['Climate Identifier'] + ' in ' + match[0]['Year'][0]
            f, axarr = plt.subplots(3, 1, sharex = True)
            for subplot in range(3):
                analysis = calc_that(match[0], subplot)
                plot_maker(analysis, axarr, subplot, subplot)
            
            f.subplots_adjust(hspace=0.25)
            f.text(0.5, 0.04, 'Day of Year', ha = 'center', va = 'center')
            stationplace = match[0]['Station Name'] + ' Station'
            f.text(0.5, 0.96, stationplace, ha = 'center', va = 'center')
        else:
            print 'This should never happen.'
               
        plt.show()
    
    return None


if __name__ == "__main__":
    '''
    For debugging purposes.
    '''
    daily_stations()
