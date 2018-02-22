#!/bin/bash

station_list='5389 5415 5441 5406 5452 5444 5373 5358 5538 5369 5401 5322 5368 5339 5327 5502 10761 48374 51157 30165 10843 10762 10815 47587 5397 48371'
year_list='2015 2016 2017'
month_list='1 2 3 4 5 6 7 8 9 10 11 12'

for station in $station_list;do for year in $year_list; do for month in $month_list;do wget --content-disposition "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=${station}&Year=${year}&Month=$month&Day=1&timeframe=1&submit=Download+Data";done;done;done
