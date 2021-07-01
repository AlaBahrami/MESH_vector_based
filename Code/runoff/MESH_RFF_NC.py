# -*- coding: utf-8 -*-
"""
NAME
    MESH_RFF_NC 
PURPOSE
    The purpose of this script is to read MESH extracted RFF, reorder it to be
    configurable to with  network_topology file, and save it in the NetCDF format
    that can be read in mizuroute program
     
PROGRAMMER(S)
    Ala Bahrami
REVISION HISTORY
    20210628 -- Initial version created and posted online
    
See also 
     summa_reindex   
    
REFERENCE 
    
"""
# %% import modules 
import os
import numpy as np
import xarray as xs
import pandas as pd
import geopandas as gpd
from datetime import date
from   summa_reindex import new_rank_extract

# %% input files 
input_ddb          = 'Input/network_topology_Fraser.nc'
input_rff_fraser   = 'Input/Fraser_RFF_D_vector.csv'
output_rff         = 'Output/Fraser_distributed_default_timestep.nc'

# %% calling the new_rank_extract
new_rank, drainage_db = new_rank_extract(input_ddb)

# %% reading the network topology file 
network_topo = xs.open_dataset(input_ddb)
network_topo.close()

# %% Seg_ids 
segid = network_topo['seg_id'].values
segid2 = drainage_db['seg_id'].values

#%% the ordering MESH rff is based on indices 
n = len(segid)
ind = []

for i in range(n):
    fid = np.where(segid2 == segid[i])[0]
    ind = np.append(ind, fid)

ind = np.int32(ind)  

# %% reading MESH runoff 
rff  = pd.read_csv(input_rff_fraser, header = None)
rff_reorder = rff.values[:,ind]

# convert MESH daily rff to mm/s
rff_reorder = rff_reorder/86400

#%% time index 

tt = pd.date_range(start='9/1/2004', end='8/31/2017', freq='D')

# %% create netcdf rff dataset

rff_ds = xs.Dataset(
    {
     "RUNOFF": (["time", "hru"], rff_reorder.astype(float)),
     },
    coords={
        "time" : (["time"], tt),
        "hru" : (["hru"], segid),
    },
)

# meta data attributes 
rff_ds['RUNOFF'].attrs.update(_FillValue = -999)
rff_ds['time'].encoding['calendar'] = 'standard'
rff_ds['time'].attrs.update(standard_name = 'time')
                            
rff_ds.attrs['Conventions'] = 'CF-1.6'
rff_ds.attrs['License']     = 'The data were written by Ala Bahrami'
rff_ds.attrs['history']     = 'Created on June 29, 2021'
rff_ds.attrs['featureType'] = 'timeSeries' 

rff_ds.to_netcdf(output_rff)