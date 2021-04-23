# -*- coding: utf-8 -*-
"""
Name
    lc_vectorbased
Purpose
    The purpose of this script is to calculate land cover fractions for each 
    subbasin of interest. Then the landcover is converted the (subbasin*lc_types).  
Programmer(s)
    Ala Bahrami
Revision History
    20210422 -- Initial version created    
See also 
    lc_extract.py    
Reference 
    
"""
# %% importing modules 
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xs
from   datetime import date
from   summa_reindex import new_rank_extract

# %% directory of input files
in_lc       = 'D:/Basin_setups/BowBanff/LC/intersect_output/bow_NALCMS_LC_intersect.shp'
input_ddb   = 'D:/programing/python/vector_based_routing/Input/network_topology_Bow_Banff.nc'
out_lc      = 'D:/programing/python/vector_based_routing/Output/MESH_LC_FRAC.nc'

# %% reading the input landcover
lc = gpd.read_file(in_lc)

# showing the lc 
fig, ax1 = plt.subplots(1,1, figsize = (10, 10))
lc.plot(ax = ax1, facecolor = 'None', edgecolor = 'red')

# %% calling the new_rank_extract
new_rank, drainage_db = new_rank_extract(input_ddb)

# %% land class types 
lc_type = ['Urban','Glacier','Barrenland','Cropland','Grass','Forest','Water']

# %% verify list of lc types
m = len(lc_type) + 1
st = [];
for i in (range(1,m)):
    st1 =   'NALCMS'+'_'+ str(i)
    st = np.append(st, st1)
    fid = np.where(lc.columns == st1)[0]
    if (fid.size == 0):
        print ('land cover %s is not the list of extracted histogram' % lc_type[i-1])

# adding lancover dump
st1 =   'NALCMS'+'_'+ 'Dump'
st = np.append(st, st1)    

# %% extract indices of lc based on the drainage database
n = len(drainage_db.hruid)
ind = []
hruid =  drainage_db.variables['hruid']

for i in range(n):
    fid = np.where(np.int32(lc['COMID'].values) == hruid[i].values)[0]
    ind = np.append(ind, fid)

ind = np.int32(ind)    

#%% calculate fractions
# reorder lc dataframe based on MESH RANK 
lc_frac = lc.values[ind , 4 : 10]
lc_frac = np.append(lc_frac, np.zeros((n , 1)) , axis = 1)

lc_sum = np.sum(lc_frac, axis = 1)
lc_sum = np.transpose(np.tile(lc_sum, (7,1)))

lc_frac = np.divide(lc_frac, lc_sum)

# Note : the summation of some subbasins does not exactly eqaul to 1 in some subbasins

# %% convert the lc_frac as a dataset and save it as netcdf
lon = drainage_db['lon'].values
lat = drainage_db['lat'].values
tt = drainage_db['time'].values

lc_ds =  xs.Dataset(
    {
        "lc_frac": (["subbasin", "lc_type"], lc_frac),
    },
    coords={
        "lon": (["subbasin"], lon),
        "lat": (["subbasin"], lat),
        "time": tt,
    },
)

# meta data attributes 
lc_ds.attrs['Conventions'] = 'CF-1.6'
lc_ds.attrs['License']     = 'The data were written by Ala Bahrami'
lc_ds.attrs['history']     = 'Created on April 23, 2021'
lc_ds.attrs['featureType'] = 'point'          

# editing lat attribute
lc_ds['lat'].attrs['standard_name'] = 'latitude'
lc_ds['lat'].attrs['units'] = 'degrees_north'
lc_ds['lat'].attrs['axis'] = 'Y'
 
# editing lon attribute
lc_ds['lon'].attrs['standard_name'] = 'longitude'
lc_ds['lon'].attrs['units'] = 'degrees_east'
lc_ds['lon'].attrs['axis'] = 'X'

# editing time attribute
lc_ds['time'].attrs.update(standard_name = 'time', 
                                 units = ('days since %s 00:00:00' % date.today().strftime('%Y-%m-%d')), axis = 'T')

# coordinate system
lc_ds['crs'] = drainage_db['crs'].copy()

# %% Save the new dataset to file.
lc_ds.to_netcdf(out_lc)


