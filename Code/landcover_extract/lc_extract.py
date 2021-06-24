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
    1_intersect_modis_tif_and_merit_hydro_shape.py written by Wouter    
Reference 
    https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/rasteranalysis.html#zonal-histogram

todo: run the QGIS processing in python instead of running directly in QGIS 
check  Wouter's code for this processing 
https://github.com/CH-Earth/summaWorkflow_public/blob/master/5_model_input/SUMMA/1_topo/1_find_HRU_elevation.py
and   qgis cookbook how to activate the pyqgis 
https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/intro.html      
"""
# %% import module 
import processing
# import qgis.core
# import os
# from shutil import which
# from qgis.core import QgsApplication
# from qgis.core import QgsVectorLayer
# from qgis.core import QgsRasterLayer
# from qgis.analysis import QgsZonalStatistic


# %% run the algorithm 
# processing.run("native:zonalhistogram" , {'COLUMN_PREFIX' : 'NALCMS_',
#             'INPUT_RASTER' : 'D:/Basin_setups/BowBanff/LC/BowBanff_LC_NALCMS_30M_SlopAsp_11GRU.tif', 
#             'INPUT_VECTOR' : 'D:/Basin_setups/BowBanff/Basin/Summa/bow_distributed.shp', 
#             'OUTPUT' : 'D:/Basin_setups/BowBanff/LC/intersect_output/bow_NALCMS_LC_intersect_11GRU.shp', 
#             'RASTER_BAND' : 1 })

processing.run("native:zonalhistogram" , {'COLUMN_PREFIX' : 'NALCMS_',
            'INPUT_RASTER' : 'D:/Fraser/LCC/fraser_extends_2010/images/classified/12/NALCMS_LC_2010_30M_clip_12class.tif', 
            'INPUT_VECTOR' : 'D:/Fraser/Basin_Boundary/easymore/FRASER_08MH126_cat_fixgeo.shp', 
            'OUTPUT' : 'D:/Fraser/LCC/fraser_extends_2010/images/Fraser_NALCMS_LC_intersect_12GRU.shp', 
            'RASTER_BAND' : 1 })
