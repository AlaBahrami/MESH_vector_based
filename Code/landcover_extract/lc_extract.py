# -*- coding: utf-8 -*-
"""
Name
    lc_vectorbased
Purpose
    The purpose of this script is to calculate zonal histogram of the desired 
    landcover types that spans over the a basin of interest. Here we have two 
    inputs, including the the NALCMS land cover and a shape file of the subbasins
 
Programmer(s)
Revision History
        
See also 
        
Reference 
    1_intersect_modis_tif_and_merit_hydro_shape.py written by Wouter
    
"""
# %% import module 
import processing

# %% run the algorithm 
processing.run("native:zonalhistogram" , {'COLUMN_PREFIX' : 'NALCMS_',
            'INPUT_RASTER' : 'D:/Basin_setups/BowBanff/LC/res90_reclass_domain_landcover_30m_buffered_glaciers.tif', 
            'INPUT_VECTOR' : 'D:/Basin_setups/BowBanff/Basin/Summa/bow_distributed.shp', 
            'OUTPUT' : 'D:/Basin_setups/BowBanff/LC/intersect_output/bow_NALCMS_LC_intersect.shp', 
            'RASTER_BAND' : 1 })
