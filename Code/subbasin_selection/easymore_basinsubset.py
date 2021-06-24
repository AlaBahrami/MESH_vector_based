# -*- coding: utf-8 -*-
"""
NAME
    easymore_basinsubset 
PURPOSE
    The purpose of this script is to extract subbbasin for a domain of interest
    based on MeritHydro subbasin and river network shape files. 
PROGRAMMER(S)
    Shervan Gharari
REVISION HISTORY
    20210601 -- Initial version created and posted online
    
REFERENCE 
    https://github.com/ShervanGharari/EASYMORE    
"""
#%% load modules
from easymore.easymore import easymore
import geopandas as gpd
import numpy as np

#%% assigning input files 
input_basin = 'D:/Data/Basin/MeritHydro/MERIT_Hydro_basin_bugfixed/78/cat_pfaf_78_MERIT_Hydro_v07_Basins_v01_bugfix1.shp'
input_river = 'D:/Data/Basin/MeritHydro/MERIT_Hydro_river/78/rivEndoMERITpfaf_78.shp'

outdir_basin = 'D:/Fraser/Basin_Boundary/easymore/'
outdir_river = 'D:/Fraser/Streamflow/easymore/'

#%% initializing easymore object
esmr = easymore()
# load the files and calculating the downstream of each segment
riv  = gpd.read_file(input_river)
cat    = gpd.read_file(input_basin) 
# get all the upstream
seg_IDs  = np.array(riv.COMID)
down_IDs = np.array(riv.NextDownID)
NTOPO    = esmr.get_all_downstream (seg_IDs,down_IDs) # this NTOPO can be caluclated once for a given code, e.g.78

# %% identify target segment ID

esmr.case_name = 'FRASER_08MH126'
target_segment = 78011863 # the segment on 08MH126, but a bit farther to be cosistent with GK
up_subbasins = esmr.get_all_upstream(target_segment,NTOPO) # segment ID
# subset
cat_up = cat.loc[cat['COMID'].isin(up_subbasins)]
riv_up = riv.loc[riv['COMID'].isin(up_subbasins)]
# plot
cat_up.plot()
riv_up.plot()
# save
cat_up.to_file(outdir_basin+esmr.case_name+'_cat.shp')
riv_up.to_file(outdir_river+esmr.case_name+'_riv.shp')