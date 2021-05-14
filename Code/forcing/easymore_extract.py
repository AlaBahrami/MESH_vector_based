# -*- coding: utf-8 -*-
"""
NAME
    easymore_extarct 
PURPOSE
    The purpose of this script is to read gridded input forcing and convert it 
    to basin-averaged forcing which is required for the vector-based version of 
    MESH model 
PROGRAMMER(S)
    Ala Bahrami
REVISION HISTORY
    20210512 -- Initial version created and posted online
    
REFERENCE 
    https://github.com/ShervanGharari/EASYMORE    
"""

#%% load module 
from easymore.easymore import easymore
import os
import numpy as np
import xarray as xs
import pandas as pd

# %% initializing EASYMORE object
esmr = easymore()

# specifying EASYMORE objects
# name of the case; the temporary, remapping and remapped file names include case name
esmr.case_name                = 'bow_banff'              
# temporary path that the EASYMORE generated GIS files and remapped file will be saved
esmr.temp_dir                 = 'D:/programing/python/MESH/forcing/'
# name of target shapefile that the source netcdf files should be remapped to
esmr.target_shp               = 'D:/programing/python/MESH/forcing/input/bow_distributed.shp'
# name of netCDF file(s); multiple files can be specified with *
#esmr.source_nc                = 'D:/programing/python/MESH/forcing/input/ERA5_NA_*.nc'
esmr.source_nc                 =  'D:/Basin_setups/BowBanff/MESH/gridded_based/forcing/RDRS/MESH_RDRSV2_input_200001_201801.nc'
# name of variables from source netCDF file(s) to be remapped
#esmr.var_names                = ['airtemp','pptrate']
esmr.var_names                 = ['RDRS_v2_A_PR0_SFC', 'RDRS_v2_P_FI_SFC',
                                  'RDRS_v2_P_FB_SFC','RDRS_v2_P_TT_09944',
                                  'RDRS_v2_P_UVC_09944','RDRS_v2_P_P0_SFC',
                                  'RDRS_v2_P_HU_09944']
# rename the variables from source netCDF file(s) in the remapped files;
# it will be the same as source if not provided
#esmr.var_names_remapped       = ['temperature','precipitation']
esmr.var_names_remapped       = ['PR','FI','FB','TT','UV','P0','HU']
# name of variable longitude in source netCDF files
#esmr.var_lon                  = 'longitude'
esmr.var_lon                  = 'lon'
# name of variable latitude in source netCDF files
esmr.var_lat                  = 'lat'
#esmr.var_lat                  = 'latitude'
# name of variable time in source netCDF file; should be always time
esmr.var_time                 = 'time'
# location where the remapped netCDF file will be saved
esmr.output_dir               = 'D:/Basin_setups/BowBanff/MESH/gridded_based/forcing/RDRS/'
# format of the variables to be saved in remapped files,
# if one format provided it will be expanded to other variables
esmr.format_list              = ['f4']
# fill values of the variables to be saved in remapped files,
# if one value provided it will be expanded to other variables
esmr.fill_value_list          = ['-9999.00']
# if required that the remapped values to be saved as csv as well
esmr.save_csv                 = False
# if uncommented EASYMORE will use this and skip GIS tasks
# esmr.remap_csv                = '../temporary/ERA5_Medicine_Hat_remapping.csv'

#%% execute EASYMORE
# Note:  remapped forcing has the precision of float32 
esmr.nc_remapper()
