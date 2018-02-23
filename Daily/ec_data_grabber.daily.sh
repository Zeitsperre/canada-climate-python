#!/bin/bash

station_list='5441 5406 5389 5444 5452 5373 5358 5538 5369 5368 5401 5322 5339 5327 5502 51157 10761 48374 30165 10843 10762 10815 47587 48371 5397'
year_list='2015 2016 2017'

for station in $station_list;do for year in $year_list;do wget --content-disposition "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=${station}&Year=${year}&Month=1&Day=1&timeframe=2&submit=Download+Data";done;done
