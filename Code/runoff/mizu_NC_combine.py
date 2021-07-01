"""
Name
    mizu_NC_combine
Purpose
    The purpose of this script is to read the time series of mizuroute routing 
    concat them to together.  
Programmer(s)
    Ala Bahrami
Revision History
    20210629 -- Initial version created and posted online 
See also     
Reference 
"""
# %% impporting module 
import os
import numpy as np
import xarray as xs
import pandas as pd
import matplotlib.pyplot as plt

#%% define I/O dirs
output_rout = 'D:/Fraser/MESH/mizuroute/output/fraser_distributed_flow_routed_2004-2017.nc'

# %% time information of datasets
# tt2 = pd.date_range(start='9/1/2004', end='8/31/2017', freq='D')

# %% define input and output variables 

ds = xs.open_mfdataset('D:/Fraser/MESH/mizuroute/output/fraser_distributed_*.nc',
                       combine = 'by_coords', concat_dim="time", data_vars="minimal")

#%% extract routing for fraser 
# kwtrout_fraser = ds['KWTroutedRunoff'].values
# kwtrout_fraser = kwtrout_fraser[:,new_rank]

# irfrout_fraser =  ds['IRFroutedRunoff'].values
# irfrout_fraser =  irfrout_fraser[: , new_rank]

# tt = ds['time'].values

# #%% plotting fraser runoff example 
# # todo : create subplots
# fig, ax = plt.subplots()
# ax.plot(tt[5:len(tt) - 1], kwtrout_fraser[5:len(tt) - 1 , 4876-1], label = 'KWTrout')
# ax.plot(tt[5:len(tt) - 1], irfrout_fraser[5:len(tt) - 1 , 4876-1], label = 'IRFrout')

# # setting label 
# ax.set_xlabel('time [days]', fontsize = 14, fontweight='bold')
# ax.set_ylabel('Outflow [$m^3$/s]', fontsize = 14, fontweight='bold')
# ax.set_title('Fraser Runoff Rank 4876', fontsize = 16, fontweight='bold')

# # axis setting 
# ax.xaxis.set_tick_params(labelsize = 13)
# ax.yaxis.set_tick_params(labelsize = 13)

# # adding grid 
# ax.grid()

# # xlim set 
# plt.xlim([tt[5], tt[len(tt) - 1]])

# # add legend
# ax.legend(prop={"size":14})

# save figure 
# plt.savefig("Output/Rank_4876_outflow.png", dpi=150, facecolor='w', edgecolor='w',
#         orientation='portrait', papertype=None, format='png',
#         transparent=False, bbox_inches=None, pad_inches=0.1,
#         frameon=None, metadata=None)


# %% write the output to a netcdf format
ds.to_netcdf(output_rout)