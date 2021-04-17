# -*- coding: utf-8 -*-
"""
NAME
    Summa forcing 
PURPOSE
    The purpose of this script is to extract SUMMA forcing files and reorder 
    them based new_rank, then save them to a netcdf format that can be read by 
    MESH model
PROGRAMMER(S)
    Ala Bahrami
REVISION HISTORY
    20210414 -- Initial version created and posted online
    20210414 -- 
REFERENCES

"""

# %% importing module 
import os
import numpy as np
import xarray as xs
import datetime
from   datetime import datetime, date, timedelta
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
from   summa_reindex import new_rank_extract

# %% define input file 
input_ddb   = 'D:/programing/python/vector_based_routing/Input/network_topology_Bow_Banff.nc'
input_forc  = 'D:/Vector_based_routing/SUMMA/summa_inputs/forcing/SUMMA_input_2000-10.nc'
output_forc = 'D:/Vector_based_routing/SUMMA/summa_inputs/forcing/MESH_input_2000-10.nc'

# %% calling the new_rank_extract 
new_rank, drainage_db = new_rank_extract(input_ddb)

# %% reading input forcing, drop non-required variables, extarct variable over time 
sum_forc = xs.open_dataset(input_forc, drop_variables=['data_step', 'hruId'])
# sum_forc = xs.open_dataset(input_forc)
sum_forc.close()
print(sum_forc.variables.keys())

#%% reorder input forcing based on new_rank
for m in ['lat','lon']:
    sum_forc[m].values = sum_forc[m].values[new_rank]
for n in ['pptrate', 'SWRadAtm','LWRadAtm','airtemp','windspd','airpres','spechum']:
    if (sum_forc[n].dims[0] == 'time'):
        sum_forc[n].values = sum_forc[n].values[: , new_rank]
    else:
        sum_forc[n].values = sum_forc[n].values[new_rank , :]

for n in ['pptrate', 'SWRadAtm','LWRadAtm','airtemp','windspd','airpres','spechum']:

    # Transpose 'averageRoutedRunoff' to match the desired order of dimensions.
    if (sum_forc[n].dims[0] == 'time'):
        v = sum_forc[n].values.transpose()
    else:
        v = sum_forc[n].values
    
    # Define the xarray.
    forc = xs.DataArray(v, coords = dict(time = (['time'], 
         sum_forc['time'].values.copy()), lat = (['subbasin'], 
         drainage_db['lat'].values.copy()), lon = (['subbasin'], 
         drainage_db['lon'].values.copy())), dims = ['subbasin', 'time'])
      
    # Update the forcing attributes (including the updated units).
    forc.attrs.update(units = sum_forc[n].units, grid_mapping = 'crs')
     
    # Override the encoding of forcing variable to specify 'time' in the list of 'coordinates' (omitted if done automatically).
    forc.encoding['coordinates'] = 'time lon lat'
     
    # Create a new data file using fields from 'drainage_db'.
    data_out = xs.Dataset({n: forc}, attrs = dict(Conventions = 'CF-1.6', featureType = 'timeSeries'))
     
    # Update attributes.
    data_out['time'].attrs.update(standard_name = 'time', axis = 'T')
    data_out['lat'].attrs.update(standard_name = 'latitude', units = 'degrees_north', axis = 'Y')
    data_out['lon'].attrs.update(standard_name = 'longitude', units = 'degrees_east', axis = 'X')
     
    # Override the encoding of 'time' to specify a 'gregorian' calendar (MESH might not recognize 'proleptic_gregorian').
    data_out['time'].encoding['calendar'] = 'gregorian'
     
    # Define a variable for the points and set the 'timeseries_id' (required for some viewers).
    data_out['subbasin'] = (['subbasin'], drainage_db['seg_id'].values.astype(np.int32).astype('S20'))
    data_out['subbasin'].attrs['cf_role'] = 'timeseries_id'
     
    # Copy 'crs' from 'drainage_db'.
    data_out['crs'] = drainage_db['crs'].copy()
     
    # Override the file 'encoding' to define 'time' as an 'UNLIMITED' dimension.
    data_out.encoding.update(unlimited_dims = 'time')

# %% save netcdf to an output 
#sum_forc.to_netcdf(output_forc)


