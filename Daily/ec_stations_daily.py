#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 10:05:19 2018
@author: trevor

convert function developed by Richie Hindle
https://stackoverflow.com/questions/1254454/fastest-way-to-convert-a-dicts-keys-values-from-unicode-to-str/1254499#1254499
"""
import os
import codecs #Needs to be removed. Obsolete
import sys
import unicodecsv as csv
import matplotlib.pyplot as plt
import collections
import numpy as np
from datetime import datetime as dt
from pdb import set_trace as stop


def convert(data):
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

    
def period(dataframe):
    """
    Determines the lenth of year in days. Needed for leap-year handling.
    """
    period = np.array(dataframe['Date/Time'], dtype='datetime64[D]')
    year = period[0].astype('datetime64[Y]').astype(str)
    return year, period


def temp(dataframe):
    """
    Formats the min and max temperature series and creates labels
    """
    year, days = period(dataframe)
    key1 = 'Min Temp (C)'
    key2 = 'Max Temp (C)'
    min_temp_raw = dataframe[key1]
    max_temp_raw = dataframe[key2]
    
    for count, factor in enumerate(min_temp_raw): #Handling NoneTypes
        try:
            factor = float(factor)
        except (TypeError, ValueError): 
            min_temp_raw[count] = 'NaN'            
    
    min_temp = np.array(min_temp_raw, dtype = np.float)
    min_temp_masked = np.ma.masked_where(np.isnan(min_temp), min_temp)

    if type(np.nansum(min_temp_masked)) != np.float64:
        return False, 'Temperature Min/Max', year

    for count, factor in enumerate(max_temp_raw): #Handling NoneTypes
        try:
            factor = float(factor)
        except (TypeError, ValueError): 
            max_temp_raw[count] = 'NaN'            
     
    max_temp = np.array(max_temp_raw, dtype = np.float)
    max_temp_masked = np.ma.masked_where(np.isnan(max_temp), max_temp)

    y1 = min_temp_masked
    y2 = max_temp_masked
    emint, emaxt = y1.min(), y2.max()
    title = 'Temperature'
    y1_label = 'Deg C'
    y2_label = None
    y1_title = 'Extreme Min Temp: {}'.format(emint)
    y2_title = 'Extreme Max Temp: {}'.format(emaxt)
    
    return days, y1, y2, year, title, y1_label, y2_label, y1_title, y2_title

def precip(dataframe):
    """
    Calculates and formats value indicators for precipitation and snow.
    """
    year, days = period(dataframe)
    key1 = 'Total Precip (mm)'
    key2 = 'Snow on Grnd (cm)'
    tot_ppt_raw = dataframe[key1]
    snow_raw = dataframe[key2]

    for count, factor in enumerate(tot_ppt_raw): #Handling NoneTypes
        try:
            factor = float(factor)
        except (TypeError, ValueError): 
            tot_ppt_raw[count] = 'NaN'            
    
    tot_ppt = np.array(tot_ppt_raw, dtype = np.float)
    tot_ppt_masked = np.ma.masked_where(np.isnan(tot_ppt), tot_ppt)

    for count, factor in enumerate(snow_raw): #Handling NoneTypes
        try:
            factor = float(factor)
        except (TypeError, ValueError): 
            snow_raw[count] = 'NaN'            
    
    snow = np.array(snow_raw, dtype = np.float)
    snow_masked = np.ma.masked_where(np.isnan(snow), snow)

    if type(np.nansum(tot_ppt_masked)) != np.float64 and\
        type(np.nansum(snow_masked)) != np.float64:
        return False, key1 + ' and ' + key2, year
    elif type(np.nansum(tot_ppt_masked)) != np.float64:
        return False, key1, year
    elif type(np.nansum(snow_masked)) != np.float64:
        return False, key2, year

    y1 = tot_ppt_masked
    y2 = snow_masked
    max_snow, sum_ppt = y2.max(), np.nansum(y1)
    title = 'Precipitation and Snow on Ground'
    y1_label = 'mm'
    y2_label = 'cm'
    y1_title = 'Day with Most Snow on Ground: {} cm'.format(max_snow)
    y2_title = 'Total Annual Precipitation: {} mm'.format(sum_ppt)

    return days, y1, y2, year, title, y1_label, y2_label, y1_title, y2_title

def ddays(dataframe, base = 10):
    """
    Calculates and formats value indicators for degree-days
    with base 10 Celsius.
    """
    def degree_days(low, high, base):
        try:
            dd = (((low + high) - base) / 2)
            dd[np.where(dd<0)] = 0
            return dd
        except RuntimeWarning:
            return 0
    
    key = 'Degree Days >' + str(base) + ' Deg C'
    year, days = period(dataframe)
    
    if temp(dataframe)[0] is False:
        return False, key, year
    
    min_temp_ma, max_temp_ma = temp(dataframe)[1:3]
    y1 = degree_days(min_temp_ma, max_temp_ma, base)
    y2 = None
    max_daily, sum_daily = y1.max(), np.nansum(y1)
    title = key
    y1_label = 'deg C'
    y2_label = None
    y1_title = 'Maximum Daily Value: {}'.format(max_daily)
    y2_title = 'Sum of Daily Values: {}'.format(sum_daily)

    return days, y1, y2, year, title, y1_label, y2_label, y1_title, y2_title

def collect_that():
    """
    Collects all files starting with "eng-daily" that are   
    located in the same directory as the script.
    """
    print "Scanning directories:\n"
    ec_stations = [ec for ec in os.listdir('.')
                   if ec.startswith('eng-daily')]
    ec_stations.sort()

    if len(ec_stations) >= 1:
        return ec_stations
    else:
        raise Exception("No stations readings were collected. Verify CSV locations.")
        sys.exit()


def place_that(name):
    """
    When given a filename will dump station location headers
    to console and return a dictionary with raw unicode keys 
    and values for station name and location variables.
    """
    try:
        location = str(name)
        with open(location, 'r') as f:
            verifier = csv.reader(f)
            for count, row in enumerate(verifier): # Read and format metadata 
                if count > 6:
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
                    key = names[0]
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
        sys.exit()
       # raise Exception("Invalid station CSV.\nVerify that CSVs hold Environment Canada station data.")


def grab_that(station):
    """
    A method that extracts climate data from CSV and converts it to a
    dictionary object.
    """
    
    with open(station, 'r') as f:
        lines = csv.reader(f)
        for i in range(25): # Skips the metadata
            next(lines)
        names, datum = [], {}
        for column in lines:
            for name in column:
                names.append(convert(name))
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

    matches = []
    order_years = [[]]
    processed_stations = []
    try:
        for i, station1 in enumerate(locations):
            if station1[ident] in processed_stations:
                continue
            matches.append([])
            matches[-1].append(station1)
            order_years[-1].append(int(station1[yr][0]))
            for station2 in locations[i + 1:]:
                if station1[ident] == station2[ident] \
                        and int(station1[yr][0]) != int(station2[yr][0]):
                    matches[-1].append(station2)
                    order_years[-1].append(int(station2[yr][0]))

            processed_stations.append(station1[ident])
        return matches
    except ValueError:
        raise Exception("Verify that CSV has valid dates and formatted properly")

def calc_that(match, plot):
    """
    A method that converts a unicode dictionary of 
    climate data to ASCII and proceeds to create a dataframe 
    derived from it.
    """
    location = match.copy()

    # Depending on the plot type being calculated, only return the variables needed
    if plot == 0:
        return temp(location)
    elif plot == 1:
        return precip(location)
    elif plot == 2:
        return ddays(location)
    else:
        return "You need more plot styles."


def plot_maker(analysis, axarr, subplot, plot):
    """
    Using plot names, axes, year and titles, creates a sublot or twin subplot.
    Is looped over to create subplots with multi-year or multi-station data.
    """
    # Import the values derived from calc_that
    try:
        days, y1, y2, year, title, y1_label, y2_label, y1_title, y2_title = analysis
    except (TypeError, ValueError):
        print analysis[1] + " for year " + analysis[2] + " is being skipped"
        return

    # General plot elements
    x = np.arange(1, len(days)+1)
    title = title + ' in ' + year
    axarr[subplot].set_title(title)
    axarr[subplot].set_xlim(min(x), max(x))
    axarr[subplot].grid(True)
        
    try:
        if plot == 0: # Create the Min and Max Temperature plot
            c1 = 'cornflowerblue'
            c2 = 'firebrick'
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, '-o', color = c1)
            axarr[subplot].plot(x, y2, '-o', color = c2)
            axarr[subplot].legend()
            
            bottom = min(y1)
            axarr[subplot].text(140, bottom+10, y1_title)
            axarr[subplot].text(140, bottom+20, y2_title)

        elif plot == 1: # Create the Snow and Precipitation plot
            c1 = 'black'
            c2 = 'royalblue'
            axarr[subplot].bar(x, y1, color = c1, edgecolor = c1)
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].tick_params('y', colors = c1)
            
            thirdpoint = (max(y1) + min(y1))/1.5
            axarr[subplot].text(140, thirdpoint, y1_title)
            
            axalt = axarr[subplot].twinx()
            axalt.plot(x, y2, 'o', color = c2)
            axalt.set_ylabel(y2_label)
            axalt.tick_params('y', colors = c2)
            
            thirdpoint = (max(y1) + min(y1))/1.5
            axalt.text(140, thirdpoint, y2_title)
            
        elif plot == 2: # Create the Degree-Days plot
            c1 = 'forestgreen'
            axarr[subplot].set_ylabel(y1_label)
            axarr[subplot].plot(x, y1, '-', color = c1)
            
            thirdpoint = (max(y1) + min(y1))/1.5
            axarr[subplot].text(15, thirdpoint, y1_title)
            axarr[subplot].text(15, thirdpoint/1.5, y2_title)
       
        else:
            return "You need more plot styles."
            
        return None

    except TypeError:
        raise Exception("That didn\'t work.")


def data_unpacker(matches, base, make_plots):
    """
    Unpacks the matches and match data to return continuous data 
    that will be appended to CSVs. If make_plots == True, will create a
    series of subplots.
    """
    csv_list = []
    dd = 'Deg Days > ' + str(base) + ' C'
    
    for match in matches:
        csv_meta = ('Station Name'
                     , 'Latitude'
                     , 'Longitude'
                     , 'Elevation'
                     , 'Climate Identifier'
                     , 'WMO Identifier'
                     , 'TC Identifier')
        csv_data = {'Date':[], 'Min Temp (C)':[], 'Max Temp (C)':[], 
                'Total Precip (mm)':[], 'Snow on Grnd (cm)':[], dd:[]}
        for keys in csv_meta:                                                                    
            csv_meta = {keys:match[0][keys]}
            csv_data.update(csv_meta)
        if len(match) > 1:
            print '\nMulti-Year Set Found; Matched as follows:'
            for iterable, station in enumerate(match):
                 print station['Station Name'] + ' ID '\
                        + station['Climate Identifier']\
                         + ' in ' + station['Year'][0]
                
            # Begin subplotting processes   
            for plot in range(3):
                if make_plots:
                    f, axarr = plt.subplots(len(match), 1, sharex = True)
                for subplot, station in enumerate(match):
                    analysis = calc_that(station, plot)
 
                    if make_plots:
                        plot_maker(analysis, axarr, subplot, plot)
                    
                    length = len(period(station)[1])
                    empty = np.ma.masked_array(np.zeros((length,)),mask=np.ones((length,)))
                    
                    # Grab formatted data as it is iterated over                          
                    if plot == 0:                     
                        csv_data['Date'].extend(period(station)[1])
                        if analysis[0] is None:
                            csv_data['Min Temp (C)'].extend(empty)
                            csv_data['Max Temp (C)'].extend(empty)    
                        else:
                            csv_data['Min Temp (C)'].extend(analysis[1])
                            csv_data['Max Temp (C)'].extend(analysis[2])
                    if plot == 1:
                        if analysis[0] is None:
                            csv_data['Total Precip (mm)'].extend(empty)
                            csv_data['Snow on Grnd (cm)'].extend(empty)
                        else:
                            csv_data['Total Precip (mm)'].extend(analysis[1])
                            csv_data['Snow on Grnd (cm)'].extend(analysis[2])
                    if plot == 2:
                        if analysis[0] is None:
                            csv_data[dd].extend(empty)
                        else:
                            csv_data[dd].extend(analysis[1])
                            
                if make_plots:            
                    f.subplots_adjust(hspace=0.25)
                    f.text(0.5, 0.04, 'Day of Year', ha = 'center', va = 'center')
                    stationplace = match[0]['Station Name'] + ' Station'
                    f.text(0.5, 0.96, stationplace, ha = 'center', va = 'center')

        elif len(match) == 1:
            station = match[0]
            print '\nSingle Year Station Found:'
            print station['Station Name'] + ' ID:' + station['Climate Identifier']\
                    + ' for ' + station['Year'][0]
            
            length = len(period(station)[1])
            empty = np.ma.masked_array(np.zeros((length,)),mask=np.ones((length,)))

            if True not in (temp(station)[0], precip(station)[0], ddays(station)[0]):
                csv_data['Date'].extend(period(station)[1])
            if temp(station)[0] is None:
                csv_data['Min Temp (C)'].extend(empty)
                csv_data['Max Temp (C)'].extend(empty)
            if precip(station)[0] is None:
                csv_data['Total Precip (mm)'].extend(empty)
                csv_data['Snow on Grnd (cm)'].extend(empty)
            if ddays(station, base)[0] is None:
                csv_data[dd].extend(empty)
                
            # Begin plotting processes
            if make_plots:            
                f, axarr = plt.subplots(3, 1, sharex = True)
            for plot in range(3):
                analysis = calc_that(station, plot)
                
                if make_plots:
                    plot_maker(analysis, axarr, plot, plot)
                
                # Grab formatted data as it is iterated over                     
                if plot == 0:
                    csv_data['Date'].extend(period(station)[1])    
                    if analysis[0] is None:
                        csv_data['Min Temp (C)'].extend(empty)
                        csv_data['Max Temp (C)'].extend(empty)    
                    else:
                        csv_data['Min Temp (C)'].extend(analysis[1])
                        csv_data['Max Temp (C)'].extend(analysis[2])
                if plot == 1:
                    if analysis[0] is None:
                        csv_data['Total Precip (mm)'].extend(empty)
                        csv_data['Snow on Grnd (cm)'].extend(empty)
                    else:
                        csv_data['Total Precip (mm)'].extend(analysis[1])
                        csv_data['Snow on Grnd (cm)'].extend(analysis[2])
                if plot == 2:
                    if analysis[0] is None:
                        csv_data[dd].extend(empty)
                    else:
                        csv_data[dd].extend(analysis[1])

            if make_plots:
                f.subplots_adjust(hspace=0.25)
                f.text(0.5, 0.04, 'Day of Year', ha = 'center', va = 'center')
                stationplace = station['Station Name'] + ' Station'
                f.text(0.5, 0.96, stationplace, ha = 'center', va = 'center')
            
        else:
            print 'This should never happen.'
        csv_list.append(csv_data)
        if make_plots:
            plt.show()
    return csv_list


def make_csvs(csv_list, base):
    """
    Writes out CSV with two headers detailing the station metadata and the
    variables being written out. If a file for an existing station exists,
    subsequent years will be appended to the file.
    """
    now = dt.now()    
    dd = 'Deg Days > ' + str(base) + ' C'
    
    head = ('Station Name'
             , 'Province'
             , 'Latitude'
             , 'Longitude'
             , 'Elevation'
             , 'Climate Identifier'
             , 'WMO Identifier'
             , 'TC Identifier')
    body = ('Date', 'Min Temp (C)', 'Max Temp (C)'
            , 'Total Precip (mm)', 'Snow on Grnd (cm)', dd)
    
    for csv_station in csv_list:
        ident = csv_station['Climate Identifier']
        name = str(ident) + '.temp_pr_dd.' + now.strftime("%Y-%m-%d") + '.csv'
                        
        if name in os.listdir('.'):
            with codecs.open(name, 'a') as f:
                list_writer = csv.writer(f, delimiter= ',')
                list_writer.writerows(zip(*[csv_station[key] for key in body]))
        else:            
            with codecs.open(name, 'wb') as f:
                dict_writer = csv.DictWriter(f, head, extrasaction='ignore')
                dict_writer.writeheader()
                dict_writer.writerow(csv_station)        
            with codecs.open(name, 'a') as f:
                dict_writer = csv.DictWriter(f, body, extrasaction = 'ignore')
                dict_writer.writeheader()
            with codecs.open(name, 'a') as f:
                list_writer = csv.writer(f, delimiter= ',')
                list_writer.writerows(zip(*[csv_station[key] for key in body]))
                

def daily_stations(base, make_plots):
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
        print len(fnames), "station readings gathered"
    else:
        place = place_that(fnames[0])
        locations.append(place)
        print "Single station reading gathered"

    for count, station in enumerate(fnames):
        datum = grab_that(station)
        locations[count].update(datum)

    matches = match_locations(locations)
    csv_list = data_unpacker(matches, base, make_plots)
    make_csvs(csv_list, base)
      
    return 0


if __name__ == "__main__":
    """
    For debugging purposes.
    """
    try:
        base = raw_input("What base for degree-days?[10]")
        if type(base) not in (int, float):
            base = 10
    except:
        base = 10
    print 'base =', base, 'deg C'
        
    make_plots = False  
    plots = raw_input("Do you want to produce plots of data? y/[n]")
    if plots in ('y', 'Y'):
        make_plots = True
    print "Making Plots!"*make_plots
    
    daily_stations(base, make_plots)
