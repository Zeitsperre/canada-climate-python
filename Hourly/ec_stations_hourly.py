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
import numpy as np
from pdb import set_trace as stop


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
        raise Exception("Not a valid station CSV. \
            Verify that CSV holds Environment Canada station data.")
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
    year = 'Year'
    month = 'Month'    
    
    matches = []
    order_months = [[]]
    processed_stations = []
    try:
        for i, station1 in enumerate(locations):
            if station1[ident] in processed_stations:
                continue
            matches.append([])
            matches[-1].append(station1)
            order_months[-1].append(int(station1[month][0]))
            for station2 in locations[i + 1:]:
                if station1[ident] == station2[ident] \
                        and int(station1[year][0]) == int(station2[year][0]) \
                                and int(station1[month][0]) != int(station2[month][0]):
                    matches[-1].append(station2)
                    order_months[-1].append(int(station2[month][0]))
            processed_stations.append(station1[ident])
            matches[-1] = [x for _, x in sorted(zip(order_months[-1], matches[-1]))]
        
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
            except AttributeError:
                continue

    def out_period(dataframe):
        """
        Determines the earliest and latest dates and returns the length of Month
        in hours total.
        """
        min_date = np.datetime64(min(dataframe['Date/Time']))
        max_date = np.datetime64(max(dataframe['Date/Time']))
        month = (dataframe['Month'][0])
        period = np.arange(min_date, max_date, dtype='datetime64[h]')

        return month, period

    def out_humid(dataframe):
        """
        Formats the indicators for Relative Humidity.
        """
        month, period = out_period(dataframe)

        humid = np.array(dataframe['Rel Hum (%)'], dtype = np.float)
        humid = np.ma.masked_where(np.isnan(humid), humid)

        x = np.arange(0, len(period)+1)
        y1 = humid
        y2 = None
        hu_min, hu_max = y1.min(), y1.max()
        title = 'Relative Humidity'
        y1_label = '%'
        y2_label = None
        y1_title = 'Monthly Min Humidity: {}'.format(hu_min)
        y2_title = 'Monthly Max Humidity: {}'.format(hu_max)
        
        return x, y1, y2, month, title, y1_label, y2_label, y1_title, y2_title

    def out_windchill(dataframe):
        """
        Summarizes the indicators for Wind Chill Factor.
        """
        month, period = out_period(dataframe)
        
        wcf_raw = dataframe['Wind Chill']
        for count, factor in enumerate(wcf_raw): #Handling those annoying NoneTypes
            try:
                factor = float(factor)
            except (TypeError, ValueError): 
                wcf_raw[count] = 'NaN'
                
        wcf = np.array(wcf_raw, dtype = np.float)
        wcf = np.ma.masked_where(np.isnan(wcf), wcf)

        x = np.arange(0, len(period)+1)
        y1 = wcf
        y2 = None
        min_wcf, mean_wcf = y1.min(), y1.mean()
        title = 'Wind Chill Factor'
        y1_label = 'Degrees Celsius'
        y2_label = None
        y1_title = 'Monthly Extreme Wind Chill: {} degrees'.format(min_wcf)
        y2_title = 'Mean Monthly Wind Chill: {} degrees'.format(mean_wcf)

        return x, y1, y2, month, title, y1_label, y2_label, y1_title, y2_title
        
    # Depending on the plot type being calculated, only return the variables needed
    if plot == 0:
        humid = out_humid(location)    
        return humid
    elif plot == 1:
        wchill = out_windchill(location)
        return wchill
    else:
        return 'Gonna need more than that'


def plot_maker(analysis, axarr, subplot, plot):
    """
    Using plot names, axes, year and titles, creates a sublot or twin subplot.
    Is looped over to create subplots with multi-year or multi-station data.
    """
    # Import the values derived from calc_that
    try:
        x, y1, y2, month, title, y1_label, y2_label, y1_title, y2_title = analysis
    except (TypeError, ValueError):
        try:
            print analysis[0] + "for Month" + analysis[1] + "is being skipped"
        except:
            print "Unskippable Error. Abandon Ship!"
            sys.exit()
        
    # General plot elements
    title = title + ' in Month ' + month
    axarr[subplot].set_title(title)
    axarr[subplot].set_xlim(min(x), max(x))
    axarr[subplot].grid(True)

    try:
        if plot == 0: # Create the Relative Humidity plot
            c1 = 'cornflowerblue'
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, '-', color = c1)
            axarr[subplot].legend()
            
            bottom = min(y1)
            axarr[subplot].text(140, bottom+15, y1_title)
            axarr[subplot].text(140, bottom+40, y2_title)

        elif plot == 1: # Create the Wind Chill Factor plot
#            c1 = 'turquoise'
#            axarr[subplot].tick_params('y', colors = c1)
#            axarr[subplot].bar(x, y1, color = c1, edgecolor = c1)
#            axarr[subplot].set_ylabel(y1_label)
#            axarr[subplot].tick_params('y', colors = c1)
#                        
#            thirdpoint = (max(y1) + min(y1))/1.5
#            axarr[subplot].text(140, thirdpoint, y1_title)
            pass
        elif plot == 2: # Create the Degree-Days plot
#            c1 = 'forestgreen'
#            axarr[subplot].set_ylabel(y1_label)
#            axarr[subplot].plot(x, y1, '-', color = c1)
#            
#            thirdpoint = (max(y1) + min(y1))/1.5
#            axarr[subplot].text(15, thirdpoint, y1_title)
#            axarr[subplot].text(15, thirdpoint/1.5, y2_title)
            pass
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
        print len(fnames), 'station readings gathered'
    else:
        place = place_that(fnames[0])
        locations.append(place)
        print 'Single station reading gathered'

    for count, station in enumerate(fnames):
        datum = grab_that(station)
        locations[count].update(datum)

    matches = match_locations(locations)
    
    #stop()
    
    #Consider cleaning this up and turning this into its own function.    
    for match in matches:
        if len(match) > 1:
            print '\nMulti-Month Set Found; Matched as follows:'
            for station in match:
                print (station['Station Name'] + ' ID:' + station['Climate Identifier'] 
                    + ' for Month ' + station['Month'][0] + ' in ' + station['Year'][0])   
            for plot in range(3):
                f, axarr = plt.subplots(len(match), 1, sharex = True)
                for subplot, station in enumerate(match):
                    analysis = calc_that(station, plot)
                    plot_maker(analysis, axarr, subplot, plot)
                
                f.subplots_adjust(hspace=0.25)
                f.text(0.5, 0.04, 'Hour in Month', ha = 'center', va = 'center')
                stationplace = match[0]['Station Name'] + ' Station for Year ' + match[0]['Year'][0]
                f.text(0.5, 0.96, stationplace, ha = 'center', va = 'center')
        
        elif len(match) == 1:
            print '\nSingle Month Station Found:'
            print (match[0]['Station Name'] + ' ID:' + match[0]['Climate Identifier']
                + ' for Month ' + station['Month'][0] + ' in ' + match[0]['Year'][0])
            f, axarr = plt.subplots(3, 1, sharex = True)
            for subplot in range(3):
                analysis = calc_that(match[0], subplot)
                plot_maker(analysis, axarr, subplot, subplot)
            
            f.subplots_adjust(hspace=0.25)
            f.text(0.5, 0.04, 'Hour in Month', ha = 'center', va = 'center')
            stationplace = match[0]['Station Name'] + ' Station for Year ' + match[0]['Year'][0]
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
