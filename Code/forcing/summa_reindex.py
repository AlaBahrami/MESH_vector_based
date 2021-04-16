# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 15:07:21 2021
The purpose of this function is to read summa_network_topology file and extarct 
extarct new_rank. 

Reference: NC-db-Reindexing

@author: Dan & Brenden
"""
# %% import modules 
import os
import numpy as np
import xarray as xs
# from   datetime import date

def new_rank_extract(in_ddb):
        #%% reading the input DDB
        drainage_db = xs.open_dataset(in_ddb)
        drainage_db.close()
        
        # Count the number of outlets (where data is 'nan').
        outlets = np.where(np.isnan(drainage_db['tosegment'].values))[0]
        
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
                    old_next[i] = None 
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
        return(new_rank)