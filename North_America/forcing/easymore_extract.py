# -*- coding: utf-8 -*-
"""
NAME
    easymore_extarct 
PURPOSE
    The purpose of this script is to read gridded input forcing and convert it 
    to basin-averaged forcing which is required for the vector-based version of 
    MESH model 
PROGRAMMER(S) Shervan Gharari  
    
REVISION HISTORY
    20210512 -- Initial version created and posted online for the Fraser application
    20220609 -- 1) addded creation of the source file
                2) visualize the remapped forcing 
REFERENCE 
    https://github.com/ShervanGharari/EASYMORE    

See also: 

Todo1 : replace hard coded parts, variable names, saved dirs, params, etc
Todo2: tranform the visualization part to a function that can be read after calling
easymore remapping  
"""

#%% load module 
from easymore.easymore import easymore
import xarray as xr
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib

# %% initializing EASYMORE object
esmr = easymore()

# specifying EASYMORE objects
# name of the case; the temporary, remapping and remapped file names include case name
esmr.case_name                 = 'RDRS_78'              
# temporary path that the EASYMORE generated GIS files and remapped file will be saved
esmr.temp_dir                 = 'D:/Basin_setups/NA/temporary78/'
# name of target shapefile that the source netcdf files should be remapped to
esmr.target_shp                = 'D:/Data/MeritHydro/MERIT_Hydro_basin_bugfixed/NA/78/cat_pfaf_78_MERIT_Hydro_v07_Basins_v01_bugfix1_WGS84.shp'
esmr.target_shp_ID             = 'COMID'
# name of netCDF file(s); multiple files can be specified with *
esmr.source_nc                  = 'D:/Basin_setups/NA/forcing/rdrs_output/1980/rdrsv2.1_1980_0131_12.nc'                                 
# name of variables from source netCDF file(s) to be remapped
esmr.var_names                 = ['RDRS_v2.1_A_PR0_SFC', 'RDRS_v2.1_P_FI_SFC',
                                  'RDRS_v2.1_P_FB_SFC','RDRS_v2.1_P_TT_09944',
                                  'RDRS_v2.1_P_UVC_09944','RDRS_v2.1_P_P0_SFC',
                                  'RDRS_v2.1_P_HU_09944']


# rename the variables from source netCDF file(s) in the remapped files;
# it will be the same as source if not provided
#esmr.var_names_remapped       = ['RDRS_FB']
# name of variable longitude in source netCDF files
esmr.var_lon                  = 'lon'
# name of variable latitude in source netCDF files
esmr.var_lat                  = 'lat'
# name of variable time in source netCDF file; should be always time
esmr.var_time                 = 'time'
# location where the remapped netCDF file will be saved
esmr.output_dir               = 'D:/Basin_setups/NA/output78/'
# format of the variables to be saved in remapped files,
# if one format provided it will be expanded to other variables
esmr.format_list              = ['f4']
# fill values of the variables to be saved in remapped files,
# if one value provided it will be expanded to other variables
esmr.fill_value_list          = ['-9999.00']
# if required that the remapped values to be saved as csv as well
#esmr.save_csv                 = False # it produces errors when it is on
#esmr.complevel                = 9
# if uncommented EASYMORE will use this and skip GIS tasks
esmr.remap_csv                = 'D:/Basin_setups/NA/temporary78/RDRS_78_remapping.csv'

#%% Create source shapefile
# NB: activate this section when the sourc forcing netcdf file will be changed 
esmr.NetCDF_SHP_lat_lon()
# create the source shapefile for case 1 and 2 if shapefile is not provided
if (esmr.case == 1 or esmr.case == 2)  and (esmr.source_shp == ''):
    if esmr.case == 1:
        if hasattr(esmr, 'lat_expanded') and hasattr(esmr, 'lon_expanded'):
            esmr.lat_lon_SHP(esmr.lat_expanded, esmr.lon_expanded,\
                esmr.temp_dir+esmr.case_name+'_source_shapefile.shp')
        else:
            esmr.lat_lon_SHP(esmr.lat, esmr.lon,\
                esmr.temp_dir+esmr.case_name+'_source_shapefile.shp')
    else:
        esmr.lat_lon_SHP(esmr.lat, esmr.lon,\
            esmr.temp_dir+esmr.case_name+'_source_shapefile.shp')
    print('EASYMORE is creating the shapefile from the netCDF file and saving it here:')
    print(esmr.temp_dir+esmr.case_name+'_source_shapefile.shp')

shp = gpd.read_file(esmr.temp_dir+esmr.case_name+'_source_shapefile.shp')
print(shp)
shp = shp [shp['lon_s']>-179]
shp.to_file(esmr.temp_dir+esmr.case_name+'_source_shapefile.shp')

# add the source shapefile 
esmr.source_shp                =   esmr.temp_dir+esmr.case_name+'_source_shapefile.shp'
esmr.source_shp_lat            =  'lat_s' # name of column latitude in the source shapefile
esmr.source_shp_lon            =  'lon_s' # name of column longitude in the source shapefile
esmr.source_shp_ID             =  'ID_s' # name of column ID in the source shapefile

#%% execute EASYMORE
# Note:  remapped forcing has the precision of float32 
esmr.nc_remapper()

#%% visualize the output one time step source and remapped forcing 
#plot style 
# font = {'family' : 'Times New Roman',
          # 'weight' : 'bold',
          # 'size'   : 24}
# matplotlib.rc('font', **font)

# # reading the source forcing and remapped one 
# ds_source = xr.open_dataset(esmr.source_nc) # source
# ds_remapped = xr.open_dataset(esmr.output_dir+'RDRS_72_remapped_1980-01-03-13-00-00.nc') # the remap of above
# max_value = ds_remapped[esmr.var_names[3]][5].max().item()
# min_value = ds_remapped[esmr.var_names[3]][5].min().item()
# print(max_value, min_value)

# shp_target = gpd.read_file(esmr.temp_dir+ esmr.case_name + '_target_shapefile.shp') # load the target shapefile

# # first picture the source
# fig, ax = plt.subplots(figsize=(20, 20))
# ds_source[esmr.var_names[3]][5].plot.pcolormesh(x="lon", y="lat",
                                                    # add_colorbar=False,
                                                    # ax = ax,
                                                    # cmap='viridis',
                                                    # vmin=min_value,
                                                    # vmax=max_value)
# shp_target.geometry.boundary.plot(color=None,edgecolor='k',linewidth = .1, ax = ax)
# # adjust the limit based on the PFAF or can be retrieved from lat/lon info
# plt.ylim([40,65])
# plt.xlim([-100,-50])
# #plt.savefig('output/NA/'+esmr.var_names[3]+'source.png', dpi=600)

# plt.close()

# # second remapped
# fig, ax = plt.subplots(figsize=(20, 20))
# ds_source[esmr.var_names[3]][5].plot.pcolormesh(x="lon", y="lat",
                                                    # add_colorbar=False,
                                                    # ax = ax,
                                                    # cmap='viridis',
                                                    # vmin=min_value,
                                                    # vmax=max_value)
# shp_target.geometry.boundary.plot(color=None,edgecolor='k',linewidth = .1, ax = ax)

# # dataframe
# df = pd.DataFrame()
# df ['ID'] = ds_remapped.ID[:]
# df ['value'] = ds_remapped[esmr.var_names[3]][5]
# df = df.sort_values(by=['ID'])
# df = df.reset_index(drop=True)

# # shapefile
# shp_target = shp_target[shp_target['COMID'].isin(df ['ID'])]
# shp_target = shp_target.sort_values(by=['COMID'])
# shp_target = shp_target.reset_index(drop=True)

# #
# shp_target ['value'] = df ['value']
# shp_target.plot(column= 'value', edgecolor='k',linewidth = .1, ax = ax,
                                                    # vmin=min_value,

                                                    # vmax=max_value)#, legend=True)
# # adjust the limit based on the PFAF
# plt.ylim([40,65])
# plt.xlim([-100,-50])
# #plt.savefig('output/NA/'+esmr.var_names[3]+'remapped.png', dpi=600)