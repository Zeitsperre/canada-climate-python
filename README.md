# canada-climate-python

A script for extracting daily and monthly values for Environment Canada stations and outputting a handful of calculated metrics

_A work in progress: run at your own risk_ 

---

## Requires

Python2, NumPy, unicodecsv, matplotlib, wget

More to be added as code base gets larger

## Goal

- Automatic downloading of nearest station data to point of interest or boundary box
- Selectable years for daily data sets
- Outputting of new data frames as SQL-loadable CSVs
- Outputting of daily data subplot figures based on number of years collectec
- GUI

## To-Do

Finish the main code

- Python3 compatibility
- Processing Monthly CSV's
- Create functions for calculating wind chill factor
- Optimize degree-days functions to allow different baselines/formulas

