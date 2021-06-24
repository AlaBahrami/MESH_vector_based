# -*- coding: utf-8 -*-
"""
Name
    lc_vectorbased
Purpose
    The purpose of this script is to read a set of summa input focing datasets and 
    concat them to together.  
Programmer(s)
    Ala Bahrami
Revision History
    20210507 -- Initial version created and posted online 
See also 
    summa_forcing.py    
Reference 
"""
# %% impporting module 
import os
import numpy as np
import xarray as xs
import pandas as pd

#%% define I/O dirs
#output_forc = 'D:/Vector_based_routing/SUMMA/summa_inputs/forcing/merge/SUMMA_input_200210_201310.nc'
output_forc = 'D:/Fraser/MESH_Vector/Forcing/RDRS/Fraser_remapped_RDRSV2_input_200001_201801.nc'

# %% time information of datasets
#tt2 = pd.date_range(start='01/01/2000', end='01/01/2018', freq='H')

# %% define input and output variables 
# ds = xs.open_mfdataset('D:/Basin_setups/BowBanff/MESH/gridded_based/forcing/RDRS/Bow_RDRS_v2_*.nc',
#                         combine = 'by_coords', concat_dim="time", data_vars="minimal")

ds = xs.open_mfdataset('D:/Fraser/MESH_Vector/Forcing/RDRS/Fraser_remapped_*.nc',
                       combine = 'by_coords', concat_dim="time", data_vars="minimal")

# %% write the output to a netcdf format
ds.to_netcdf(output_forc)