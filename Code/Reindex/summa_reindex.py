# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 15:07:21 2021
The purpose of this function is to read summa_network_topology file and extarct 
extarct new_rank. 

Reference: NC-db-Reindexing

@author: Daniel Princz

last modified 
                06/04/2021
                1) change value of outlet from NaN to zero to be consistent with 
                network topology extracted from easymore
                6/7/2021
                1) adding minimum channel slope threshold 
"""
# %% import modules 
import os
import numpy as np
import xarray as xs
from   datetime import date

def new_rank_extract(in_ddb):
        #%% reading the input DDB
        drainage_db = xs.open_dataset(in_ddb)
        drainage_db.close()
        
        # Count the number of outlets (where data is 'nan').
        # outlets = np.where(np.isnan(drainage_db['tosegment'].values))[0]
        outlets = np.where(drainage_db['tosegment'].values == 0)[0]
        
        # %%  Re-indexing seg_id and tosegment
        # Get the segment ID associated with the outlet.
        first_index = drainage_db['seg_id'].values[outlets[0]]
         
        # Create a copy of the 'tosegment' field.
        old_next = drainage_db['tosegment'].values.copy()
         
        ## Set the current 'Next' and 'Rank' values.
        # total number of values
        current_next = len(drainage_db['seg_id']) 
        # total number of values less number of outlets
        current_rank = current_next - len(outlets) 
         
        ## Create dummy arrays for new values.
        # size of 'seg_id'
        new_next = [0]*len(drainage_db['seg_id']) 
        # empty list (to push values to)
        next_rank = [] 
        # list to append positions of new 'rank', first element is position of outlet
        new_rank = [outlets[0]] 
        
        # %% Reorder seg_id and tosegment
        while (first_index != -1):
            for i in range(len(old_next)):
                if (old_next[i] == first_index):
                    # save rank of current 'next'
                    next_rank.append(drainage_db['seg_id'].values[i]) 
                    # assign next using new ranking
                    new_next[i] = current_next 
                    # save the current position corresponding to the new 'rank'
                    new_rank.append(i) 
                    current_rank -= 1
                    # override input value to mark as completed
                    # old_next[i] = None 
                    old_next[i] = 0
                    break
            if (len(next_rank) == 0):
                    # no more IDs to process
                    first_index = -1 
            elif (not np.any(old_next == first_index)):
                # take next rank by 'next' order
                first_index = next_rank[0] 
                # drop that element from the list
                del next_rank[0] 
                # deincrement the 'next' rank
                current_next -= 1 

        new_rank = np.flip(new_rank)
        
        # %% reordering 
        for m in ['basin_area', 'length', 'slope', 'lon', 'lat', 'hruid', 
                  'seg_id', 'seg_hr_id', 'tosegment', 'width', 'manning']:
            drainage_db[m].values = drainage_db[m].values[new_rank]
 
        # Reorder the new 'Next'.
        new_next = np.array(new_next)[new_rank]
        
        # %% check if channel slope values match the minimum threshold 
        min_slope = 0.000001
        drainage_db['slope'].values[drainage_db['slope'].values < min_slope] = min_slope
        
        # %% Adding the updated Rank and Next variables to the file
        drainage_db['Rank'] = (['n'], np.array(range(1, len(new_rank) + 1), 
                              dtype = 'int32')) # ordered list from 1:NA
        drainage_db['Rank'].attrs.update(standard_name = 'Rank', 
                            long_name = 'Element ID', units = '1', _FillValue = -1)
        
        drainage_db['Next'] = (['n'], new_next.astype('int32')) # reordered 'new_next'
        drainage_db['Next'].attrs.update(standard_name = 'Next', 
                           long_name = 'Receiving ID', units = '1', _FillValue = -1)

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
        
        return new_rank, drainage_db