#!/bin/bash

station_list1='5411 5431 5490 5476 5530 5389 5452 5406 5444 5369 5401 5368 5327 5339 5397'

station_list2='5530 5397 5368'
year_list='2017'


for station in $station_list2;do for year in $year_list;do wget --content-disposition "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=${station}&Year=${year}&Month=1&Day=1&timeframe=2&submit=Download+Data";done;done
