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
new_rank = new_rank_extract(input_ddb)

# %% reading input forcing, drop non-required variables, extarct variable over time 
sum_forc = xs.open_dataset(input_forc, drop_variables=['data_step', 'hruId'])
# sum_forc = xs.open_dataset(input_forc)
sum_forc.close()
print(sum_forc.variables.keys())

#%% reorder input forcing based on new_rank
for m in ['lat','lon']:
    sum_forc[m].values = sum_forc[m].values[new_rank]
for n in ['pptrate', 'SWRadAtm','LWRadAtm','airtemp','windspd','airpres','spechum']:
    sum_forc[n].values = sum_forc[n].values[: , new_rank]

# %% save netcdf to an output 
sum_forc.to_netcdf(output_forc)


