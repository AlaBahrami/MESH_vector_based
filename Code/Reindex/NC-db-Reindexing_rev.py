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
last modified 
        6/4/2021
        1) removed reading SUMMA runoff inputs and saving to WR_runoff  
        2) change value of outlet from NaN to zero to be consistent with 
        network topology extracted from easymore
        6/7/2021
        1) adding minimum channel slope threshold 
        6/15/2021
        1) adding sanity checks to see if the reordering is applied correctly
        2) appending Rank and Next to each subbasin 
        6/22/2021
        changed the minimum slope value 
"""
#%% Required packages.
import os
import numpy as np
import xarray as xs
import geopandas as gpd
from datetime import date
import matplotlib.pyplot as plt

#%% File names.
# todo :  these inputs should be read from a parameter file 
#input_drainage_database  = 'Input/network_topology_Bow_Banff.nc'
input_drainage_database  = 'Input/network_topology_Fraser.nc'
output_drainage_database = 'Output/Fraser_MESH_drainage_database.nc'
output_parameter_file    = 'Output/Fraser_MESH_parameters.nc'
input_shp                = 'D:/Fraser/Basin_Boundary/easymore/FRASER_08MH126_cat_fixgeo.shp'
output_shp               = 'D:/Fraser/Basin_Boundary/easymore/FRASER_08MH126_cat_fixgeo_edit.shp'

# %%% Reindexing SUMMA/mizuRoute files %%%

# %% Opening and loading data from the 'topology' file 
# Checks
err = 0
 
#% Check if 'input_drainage_database' exists.
if (not os.path.exists(input_drainage_database)):
    print("ERROR: The input file cannot be found: %s" % input_drainage_database)
    err = 1 
 
# Exit if errors were found.
if (err != 0): exit()
 
# Warn if overwriting 'input_drainage_database'.
if (input_drainage_database == output_drainage_database):
    print("WARNING: Existing input file will be overwritten: %s" % input_drainage_database)
  
#% Import the drainage database then close the connection to the file.
drainage_db = xs.open_dataset(input_drainage_database)
drainage_db.close()
 
# Count the number of outlets (where data is 'nan').
# outlets = np.where(np.isnan(drainage_db['tosegment'].values))[0]
outlets = np.where(drainage_db['tosegment'].values == 0)[0] 

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
            #old_next[i] = None # override input value to mark as completed
            old_next[i] = 0
            break
    if (len(next_rank) == 0):
        first_index = -1 # no more IDs to process
    elif (not np.any(old_next == first_index)):
        first_index = next_rank[0] # take next rank by 'next' order
        del next_rank[0] # drop that element from the list
        current_next -= 1 # deincrement the 'next' rank
 
# Current order goes from lowest 'downstream' to highest 'upstream', must be flipped.
new_rank = np.flip(new_rank)

#np.savetxt(rank_data, new_rank, delimiter=",")

# %% Re-ordering variables
# Reorder the arrays using the new index (via 'new_rank').
for m in ['basin_area', 'length', 'slope', 'lon', 'lat', 'hruid', 'seg_id', 'seg_hr_id', 'tosegment', 'width', 'manning']:
    drainage_db[m].values = drainage_db[m].values[new_rank]
 
# Reorder the new 'Next'.
new_next = np.array(new_next)[new_rank]

#%% sanity check to verify the next of upstreams are defined properly and check 
# whether the reordering is applied correctly
segid = drainage_db['seg_id'].values
tosegment = drainage_db['tosegment'].values

r = np.where(tosegment == 78005280)[0]
# upstream segids
print(segid[r])

# double check the id of the downstream segid
r2 = new_next[r][0]
print(r2)
# row numbers are obtained from Rank&Next -1 
print(segid[r2-1])

# %% check if channel slope values match the minimum threshold 
min_slope = 0.000001
drainage_db['slope'].values[drainage_db['slope'].values < min_slope] = min_slope

# %% Adding the updated Rank and Next variables to the file
# Add new 'Rank' and 'Next' attributes.
# note : the Next of the outlet is zero. 

drainage_db['Rank'] = (['n'], np.array(range(1, len(new_rank) + 1), dtype = 'int32')) # ordered list from 1:NA
drainage_db['Rank'].attrs.update(standard_name = 'Rank', long_name = 'Element ID', units = '1', _FillValue = -1)
drainage_db['Next'] = (['n'], new_next.astype('int32')) # reordered 'new_next'
drainage_db['Next'].attrs.update(standard_name = 'Next', long_name = 'Receiving ID', units = '1', _FillValue = -1)

# %% reading the subbasin shape file and appending other variable and rename some variables  
shp_basin = gpd.read_file(input_shp)

n = len(segid)
ind = []

for i in range(n):
    fid = np.where(np.int32(shp_basin['COMID'].values) == segid[i])[0]
    ind = np.append(ind, fid)

ind = np.int32(ind)    

shp_basin['Rank'] = 0
shp_basin['Next'] = 0
shp_basin['ChnLengthm'] = 0.0
shp_basin['ChnlSlope']  = 0.0

shp_basin['Rank'].values[ind] = drainage_db['Rank'].values.copy()
shp_basin['Next'].values[ind] = drainage_db['Next'].values.copy()
shp_basin['ChnLengthm'].values[ind] = drainage_db['length'].values.copy() 
shp_basin['ChnlSlope'].values[ind]  = drainage_db['slope'].values.copy() 

# convert subbasin area to m2
shp_basin.unitarea *= 10.**6
shp_basin = shp_basin.rename({"unitarea" : "unitaream2"}, axis = 1)

# save geodatabase 
shp_basin.to_file(output_shp)

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