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
import pdb

def collectThat():
    '''
    Collects all files starting with "eng-" and ending with ".csv"  
    located in the same directory as the script. Need to consider 
    making a method allowing for users to feed in a directory location 
    if they want to scan a filesystem.
    '''
    print 'Scanning directories now\n' 
    ec_stations = [ec for ec in os.listdir('.') \
        if ec.startswith('eng-')]
    ec_stations.sort()

    if len(ec_stations) >= 1:
        return ec_stations
    else:
        raise Exception("No stations were collected. Verify CSV location.")
        sys.exit()

def placeThat(file):
    '''
    When given a filename will dump station location headers
    to console and return a dictionary with raw unicode keys 
    and values for station name and location variables.
    '''
    try:
        location = str(file)
        with codecs.open(location, 'rb') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            verifier = csv.reader(f, dialect)
            for count, row in enumerate(verifier):
                print ': '.join(row)
                if count > 6:
                    print '\n'
                    break
            f.seek(0)            
            names = ('Station Name'\
                ,'Province'\
                ,'Latitude'\
                ,'Longitude'\
                ,'Elevation'\
                ,'Climate Identifier'\
                ,'WMO Identifier'\
                ,'TC Identifier')
            datum = {}
            for name in names:
                datum[name] = []
            
            for count, row in enumerate(verifier):
                if count == 0:
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
    except:
        raise Exception("Not a valid station CSV. \
            Verify that CSV holds Daily values.")

def grabThat(station):
    '''
    A method that extracts climate data from CSV and converts it to a
    dictionary object.
    '''
    with codecs.open(station, 'rb',) as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        lines = csv.reader(f, dialect)
        for i in range(25):
            next(lines)
        
        names, datum = [], {}            
        for column in lines:
            for name in column:
                names.append(name)
                datum[name] = []
            break
        
        reader = csv.DictReader(f, fieldnames = names\
            , delimiter = ',', quotechar = '"')
        for row in reader:
            for column, value in row.iteritems():
                value = value
                datum.setdefault(column, []).append(value)
        return datum
        
def matchLocations(locations):
    '''
    A method to match locations that appear multiple times in the same list
    and return year-ordered lists that can then be plotted sequentially
    '''
    
    ident = 'Climate Identifier'
    year = 'Year'

    matches = []
    order_years = [[]]
    processed_stations = []
    
    for i, station1 in enumerate(locations):
        if station1[ident] in processed_stations:
            continue
        matches.append([])
        matches[-1].append(station1)
        order_years[-1].append(int(station1[year][0]))
        for station2 in locations[i+1:]:
            if station1[ident] == station2[ident]\
               and int(station1[year][0]) != int(station2[year][0]):
                matches[-1].append(station2)
                order_years[-1].append(int(station2[year][0]))
        processed_stations.append(station1[ident])
        matches[-1] = [x for _,x in sorted(zip(order_years[-1], matches[-1]))]

    return matches

def calcThat(match, plot):
    '''   
    A method that converts a unicode dictionary of 
    climate data to ASCII and proceeds to create a dataframe 
    derived from it.
    '''
    location = match
    for key in match:
        newkey = key.encode('ascii','ignore')
        location[newkey] = location.pop(key)
        for count, val in enumerate(match[newkey]):
            try:
                newval = val.encode('ascii','ignore')
                location[newkey][count] = newval
            except TypeError:
                continue
    
    def outpMinT(dataframe):
        pass
    
    def outMaxT(dataframe):
        pass
    
    def outPpt(dataframe):
        pass
    
    def outDD10(dataframe, plot):
        '''
        Calculates andformats value indicators for degree-days
        with base 10 Celsius
        '''
        def degreeDays(low, high):
            dd = (((low+high)-10)/2)
            if dd < 0:
                dd = 0
            return dd
        
        min_date = np.datetime64(min(dataframe['Date/Time']))
        max_date = np.datetime64(max(dataframe['Date/Time']))
        year = (dataframe['Year'][0])
        period = np.arange(min_date, max_date+1)
        
        max_temp_raw = np.array(dataframe['Max Temp (C)'])
        max_temp_masked = np.ma.masked_where(max_temp_raw == '', max_temp_raw)    
        max_temp = np.array([float(val) for val in max_temp_masked])
        
        min_temp_raw = np.array(dataframe['Min Temp (C)'])
        min_temp_masked = np.ma.masked_where(min_temp_raw == '', min_temp_raw)    
        min_temp = np.array([float(val) for val in min_temp_masked])

        x = np.arange(0.,len(period))
        y = map(degreeDays, min_temp, max_temp)
        max_daily, sum_daily = max(y), np.nansum(y)
        max_daily_title = 'Maximum Daily Value: {}'.format(max_daily)
        sum_daily_title = 'Sum of Daily Values: {}'.format(sum_daily)
      
        return x, y, year, max_daily_title, sum_daily_title 
 
    dd10 = outDD10(location, plot) 
    return dd10
    
def plotThat(plot, x, va, year, maxtitle, sumtitle):
    '''
    Using plot names, axes, year and titles, creates a sublot
    '''
    
#    fig, ax = plt.subplots(plot,1)
#    
#    plot.plot(x, va, 'o')
#    plot.title('Degree Days (Base 10C) for year {}'.format(year))
#    plot.xlabel('Day of Year')
#    plot.ylabel('Degree-Days (Base 10C)')
#    
#    plot.annotate(max_daily_title, xy=(30, max_daily))
#    plot.annotate(sum_daily_title, xy=(200, max_daily))
#    plt.show()    
    
    pass
    
    
    
def main():
    '''
    The main script that calls other methods; Odd calls and methods that are
    yet to be integrated are placed here to ensure script methods can be run to
    completion before they are used by other scripts.
    '''
    fnames = collectThat()
    locations = []    
    
    if len(fnames) > 1:
        for f in fnames:
            place = placeThat(f)
            locations.append(place)
        print len(fnames), 'stations gathered'
    else:
        place = placeThat(fnames[0])
        locations.append(place)
        print 'Single station gathered'

    for count, station in enumerate(fnames):
        datum = [] 
        datum = grabThat(station)
        locations[count].update(datum)
    
    matches = matchLocations(locations)

#    for match in matches:
#        if match >1:
#            plots = len(match)
#            ax = []
#            for count in match:
#                ax = 'ax'+str(count)
#
#            for count, plots in enumerate(ax):
#                plot = 'ax'+str(count)
#                
#                calcThat(match[count], plot)
#        else:
#            pass
#    
#    plt.show()    
#    
    return None

if __name__ == "__main__":
    '''
    For debugging purposes.
    '''
    main()