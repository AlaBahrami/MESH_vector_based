# -*- coding: utf-8 -*-
"""
Purpose : visualize mapped forcing generated from easymore. 
Created on Tue Jun  7 17:02:21 2022

PROGRAMMER(S)
        Ala Bahrami
See also
         easymore_extract 
"""
#%% import modules 
import xarray as xr
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

#%% input files 
fs = 'D:/Basin_setups/NA/output75/RDRS_75_remapped_1980-01-0103-13-00-00.nc'
fs_shp = 'D:/Data/MeritHydro/MERIT_Hydro_basin_bugfixed/NA/75/cat_pfaf_75_MERIT_Hydro_v07_Basins_v01_bugfix1_WGS84_edit.shp'
domain_name     = 'PFAF75' 
outdir          = 'Output/NA/'

#%% plot style 
cmaps = ['viridis','Blues_r', 'cividis', 'seismic_r']
var   = ['RDRS_v2.1_A_PR0_SFC', 'RDRS_v2.1_P_FI_SFC',
        'RDRS_v2.1_P_FB_SFC','RDRS_v2.1_P_TT_09944',
        'RDRS_v2.1_P_UVC_09944','RDRS_v2.1_P_P0_SFC',
        'RDRS_v2.1_P_HU_09944']

var2 = ['RDRS_FB','RDRS_FI','RDRS_HU','RDRS_P0','RDRS_PR0',
        'RDRS_TT','RDRS_UVC']
font = {'family' : 'Times New Roman',
         'weight' : 'bold',
         'size'   : 24}
matplotlib.rc('font', **font)

#%% visualize the remapped forcing variables 
ds = xr.open_dataset(fs)

for col in range(1): # len(var)
    fig, ax = plt.subplots(figsize=(20, 20)) 
    df = pd.DataFrame()
    df ['ID'] = ds.ID[:]
    df ['value'] = ds[var[col]][5,:]
    df = df.sort_values(by=['ID'])
    df = df.reset_index(drop=True)
    #print(df)
    
    #% setting values in the shape file  
    # shapefile
    shp = gpd.read_file(fs_shp) 
    shp = shp[shp['COMID'].isin(df ['ID'])]
    shp = shp.sort_values(by=['COMID'])
    shp = shp.reset_index(drop=True)
    shp ['value'] = df ['value']
    #print(shp)
    #print(len(shp))
    
    mn = np.min(shp ['value'])    
    mx = np.max(shp ['value'])
    tl = domain_name+'_'+var[col]+'_1980-01-01'
    ax.set_title(tl)
    ax.set_xlabel('Longitude [degree east]')            
    ax.set_ylabel('Latitude [degree north]')
    
    shp.plot(column='value', cmap=cmaps[0], edgecolor='k',linewidth=0.1,ax = ax, vmin = mn, vmax = mx) 
    plt.savefig(outdir+var[col]+'_'+domain_name+'_remaped.png', format='png', dpi=600)
    plt.close()
    
