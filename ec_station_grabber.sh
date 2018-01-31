#!/bin/bash

# Be sure to specify the stations, years, months before launching the script
# timeframe options are 1:Hourly, 2:Daily, 3:Monthly. These can be passed to the command with loop or specified in the wget query

station_list='5415'
year_list='2015 2016 2017'
month_list='1 2 3 4 5 6 7 8 9 10 11 12'
tframe='1 2 3'


for station in $station_list;do for year in $year_list; do for month in $month_list;do wget --content-disposition "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=${station}&Year=${year}&Month=$month&Day=1&timeframe=1&submit=Download+Data";done;done;done
