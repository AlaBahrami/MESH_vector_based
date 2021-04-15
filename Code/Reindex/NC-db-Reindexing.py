# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 16:03:34 2021
# Description: 'NC-db-Reindexing'
#   This script re-indexes SUMMA drainage database and data files (.nc)
#  
# Configurable conditions.
# Required:
#   - input_drainage_database:
#       Name of the input drainage database file including extension.
#   - input_data:
#       Name of the input data file including extension.
#   - output_drainage_database:
#       Name of the output drainage database file including extension
#       (e.g., 'MESH_drainage_database.nc'.
#   - output_data:
#       Name of the output data file including extension
#       (e.g., 'WR_runoff.nc').
@author: Daniel Princz
"""
#%% Required packages.
import os
import numpy as np
import xarray as xs
from datetime import date
 
#%% File names.
input_drainage_database  = 'Input/network_topology_Bow_Banff.nc'
input_data               = 'Input/bow_distributed_default_timestep.nc'
output_drainage_database = 'Output/MESH_drainage_database.nc'
output_parameter_file    = 'Output/MESH_parameters.nc'
output_data              = 'Output/WR_runoff.nc'
rank_data                = 'Output/new_rank.csv'
 
# %%% Reindexing SUMMA/mizuRoute files %%%

# %% Opening and loading data from the 'topology' file 
# Checks
err = 0
 
#% Check if 'input_drainage_database' exists.
if (not os.path.exists(input_drainage_database)):
    print("ERROR: The input file cannot be found: %s" % input_drainage_database)
    err = 1
 
# Check if 'input_data' exists.
if (not os.path.exists(input_data)):
    print("ERROR: The input file cannot be found: %s" % input_data)
    err = 1
 
# Exit if errors were found.
if (err != 0): exit()
 
# Warn if overwriting 'input_drainage_database'.
if (input_drainage_database == output_drainage_database):
    print("WARNING: Existing input file will be overwritten: %s" % input_drainage_database)
 
# Warn if overwriting 'input_data'.
if (input_data == output_data):
    print("WARNING: Existing input file will be overwritten: %s" % input_data)
 
#% Import the drainage database then close the connection to the file.
drainage_db = xs.open_dataset(input_drainage_database)
drainage_db.close()
 
# Count the number of outlets (where data is 'nan').
outlets = np.where(np.isnan(drainage_db['tosegment'].values))[0]
 
# Checks.
err = 0
if (len(outlets) == 0):
    print("ERROR: No outlets found.")
    err = 1
elif (len(outlets) != 1):
    print("ERROR: Algorithm does not support multiple outlets at this time. Routine cannot continue.")
    err = 1
 
# Exit if errors were found.
if (err != 0): exit()

# %%  Re-indexing seg_id and tosegment 
# Get the segment ID associated with the outlet.
first_index = drainage_db['seg_id'].values[outlets[0]]
 
# Create a copy of the 'tosegment' field.
old_next = drainage_db['tosegment'].values.copy()
 
# Set the current 'Next' and 'Rank' values.
current_next = len(drainage_db['seg_id']) # total number of values
current_rank = current_next - len(outlets) # total number of values less number of outlets
 
# Create dummy arrays for new values.
new_next = [0]*len(drainage_db['seg_id']) # size of 'seg_id'
next_rank = [] # empty list (to push values to)
new_rank = [outlets[0]] # list to append positions of new 'rank', first element is position of outlet
 
# Loop to re-rank values.
while (first_index != -1):
    for i in range(len(old_next)):
        if (old_next[i] == first_index):
            next_rank.append(drainage_db['seg_id'].values[i]) # save rank of current 'next'
            new_next[i] = current_next # assign next using new ranking
            new_rank.append(i) # save the current position corresponding to the new 'rank'
            current_rank -= 1
            old_next[i] = None # override input value to mark as completed
            break
    if (len(next_rank) == 0):
        first_index = -1 # no more IDs to process
    elif (not np.any(old_next == first_index)):
        first_index = next_rank[0] # take next rank by 'next' order
        del next_rank[0] # drop that element from the list
        current_next -= 1 # deincrement the 'next' rank
 
# Current order goes from lowest 'downstream' to highest 'upstream', must be flipped.
new_rank = np.flip(new_rank)

np.savetxt(rank_data, new_rank, delimiter=",")

# %% Re-ordering variables
# Reorder the arrays using the new index (via 'new_rank').
for m in ['basin_area', 'length', 'slope', 'lon', 'lat', 'hruid', 'seg_id', 'seg_hr_id', 'tosegment', 'width', 'manning']:
    drainage_db[m].values = drainage_db[m].values[new_rank]
 
# Reorder the new 'Next'.
new_next = np.array(new_next)[new_rank]

# %% Adding the updated Rank and Next variables to the file
# Add new 'Rank' and 'Next' attributes.
drainage_db['Rank'] = (['n'], np.array(range(1, len(new_rank) + 1), dtype = 'int32')) # ordered list from 1:NA
drainage_db['Rank'].attrs.update(standard_name = 'Rank', long_name = 'Element ID', units = '1', _FillValue = -1)
drainage_db['Next'] = (['n'], new_next.astype('int32')) # reordered 'new_next'
drainage_db['Next'].attrs.update(standard_name = 'Next', long_name = 'Receiving ID', units = '1', _FillValue = -1)

# %% Adding missing attributes and renaming variables
# Add 'axis' and missing attributes for the 'lat' variable.
drainage_db['lat'].attrs['standard_name'] = 'latitude'
drainage_db['lat'].attrs['units'] = 'degrees_north'
drainage_db['lat'].attrs['axis'] = 'Y'
 
# Add 'axis' and missing attributes for the 'lon' variable.
drainage_db['lon'].attrs['standard_name'] = 'longitude'
drainage_db['lon'].attrs['units'] = 'degrees_east'
drainage_db['lon'].attrs['axis'] = 'X'
 
# Add or overwrite 'grid_mapping' for each variable (except axes).
for v in drainage_db.variables:
    if (drainage_db[v].attrs.get('axis') is None):
        drainage_db[v].attrs['grid_mapping'] = 'crs'
 
# Add the 'crs' itself (if none found).
if (drainage_db.variables.get('crs') is None):
    drainage_db['crs'] = ([], np.int32(1))
    drainage_db['crs'].attrs.update(grid_mapping_name = 'latitude_longitude', longitude_of_prime_meridian = 0.0, semi_major_axis = 6378137.0, inverse_flattening = 298.257223563)
 
# Rename variables.
for old, new in zip(['basin_area', 'length', 'slope', 'manning'], ['GridArea', 'ChnlLength', 'ChnlSlope', 'R2N']):
    drainage_db = drainage_db.rename({old: new})
 
# Rename the 'subbasin' dimension (from 'n').
drainage_db = drainage_db.rename({'n': 'subbasin'})

# %% Specifying the NetCDF "featureType"
# Add a 'time' axis with static values set to today (in this case, time is not actually treated as a dimension).
drainage_db['time'] = (['subbasin'], np.zeros(len(new_rank)))
drainage_db['time'].attrs.update(standard_name = 'time', units = ('days since %s 00:00:00' % date.today().strftime('%Y-%m-%d')), axis = 'T')
 
# Set the 'coords' of the dataset to the new axes.
drainage_db = drainage_db.set_coords(['time', 'lon', 'lat'])
 
# Add (or overwrite) the 'featureType' to identify the 'point' dataset.
drainage_db.attrs['featureType'] = 'point'

# %% Saving the "MESH_drainage_database.nc" file 
# Save the updated variables to file.
drainage_db.to_netcdf(output_drainage_database)

# %%% Creating "WR_runoff.nc" from the data file %%% 

# %% reorder and save runoff data 

# Import the data then close the connection to the file.
forcing_data = xs.open_dataset(input_data)
forcing_data.close()
 
# Reorder the arrays using the new index (via 'new_rank').
for m in ['averageRoutedRunoff']:
     
    # Must consider the order of the 'time' dimension.
    if (forcing_data[m].dims[0] == 'time'):
        forcing_data[m].values = forcing_data[m].values[:, new_rank]
    else:
        forcing_data[m].values = forcing_data[m].values[new_rank, :]
 
# Transpose 'averageRoutedRunoff' to match the desired order of dimensions.
if (forcing_data['averageRoutedRunoff'].dims[0] == 'time'):
    v = forcing_data['averageRoutedRunoff'].values.transpose()
else:
    v = forcing_data['averageRoutedRunoff'].values
 
# Define the xarray.
RFF = xs.DataArray(v, coords = dict(time = (['time'], forcing_data['time'].values.copy()), lat = (['subbasin'], drainage_db['lat'].values.copy()), lon = (['subbasin'], drainage_db['lon'].values.copy())), dims = ['subbasin', 'time'])
 
# Convert the rate in [m s**-1] to amount in [mm] using the same time-stepping (hourly in this case).
RFF.values *= 1000.0*3600.0
 
# Update the 'RFF' attributes (including the updated units).
RFF.attrs.update(units = 'mm', grid_mapping = 'crs')
 
# Override the encoding of 'RFF' to specify 'time' in the list of 'coordinates' (omitted if done automatically).
RFF.encoding['coordinates'] = 'time lon lat'
 
# Create a new data file using fields from 'drainage_db'.
data_out = xs.Dataset({'RFF': RFF}, attrs = dict(Conventions = 'CF-1.6', featureType = 'timeSeries'))
 
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
 
# Save the new dataset to file.
data_out.to_netcdf(output_data)

# %%% Save "manning" (R2N) to "MESH_parameters.nc" %%% 

# %% save manning 

# Create a new data file using fields from 'drainage_db'.
parameters_out = xs.Dataset(coords = dict(lat = (['subbasin'], drainage_db['lat'].values.copy()), lon = (['subbasin'], drainage_db['lon'].values.copy())), attrs = dict(Conventions = 'CF-1.6', featureType = 'point'))
 
# Update attributes.
parameters_out['lat'].attrs.update(standard_name = 'latitude', units = 'degrees_north', axis = 'Y')
parameters_out['lon'].attrs.update(standard_name = 'longitude', units = 'degrees_east', axis = 'X')
 
# Add the same 'time' from the 'drainage_db' point file.
parameters_out['time'] = drainage_db['time'].copy()
 
# Set the 'coords' of the dataset to the new axes.
parameters_out= parameters_out.set_coords(['time', 'lon', 'lat'])
 
# Add parameters from the updated 'drainage_db'.
for m in ['R2N']:
    parameters_out[m] = drainage_db[m].copy()
 
# Copy 'crs' from 'drainage_db'.
parameters_out['crs'] = drainage_db['crs'].copy()
 
# Save the new dataset to file.
parameters_out.to_netcdf(output_parameter_file)

# Print end of script message.
print('\nProcessing has completed.')

