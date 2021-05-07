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
output_forc = 'D:/Vector_based_routing/SUMMA/summa_inputs/forcing/merge/SUMMA_input_200010_201310.nc'

# %% time information of datasets
tt = pd.date_range(start='10/01/2000', end='10/08/2013', freq='H')

# %% define input and output variables 
# ds = xs.open_mfdataset('D:/Vector_based_routing/SUMMA/summa_inputs/forcing/SUMMA_input_*.nc',
#                        combine = 'by_coords', concat_dim="time", data_vars="all")

ds = xs.open_mfdataset('D:/Vector_based_routing/SUMMA/summa_inputs/forcing/SUMMA_input_*.nc',
                       combine = 'by_coords', concat_dim="time", data_vars="minimal")

# %% write the output to a netcdf format
ds.to_netcdf(output_forc)