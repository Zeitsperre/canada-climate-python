#!/bin/bash

station_list1='5411 5431 5490 5476 5530 5389 5452 5406 5444 5369 5401 5368 5327 5339 5397'

station_list2='5406 5397 5444'
year_list='2017'
month_list='1 2 3 4 5 6 7 8 9 10 11 12'

for station in $station_list2;do for year in $year_list; do for month in $month_list;do wget --content-disposition "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=${station}&Year=${year}&Month=$month&Day=1&timeframe=1&submit=Download+Data";done;done;done
