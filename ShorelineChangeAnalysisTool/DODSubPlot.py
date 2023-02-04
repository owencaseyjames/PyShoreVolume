#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 11:28:07 2023

@author: owenjames
"""
#DODSubPlot.py

################################################################
##########               DOD Sub Plots             #############
##### Creates one subplot of DOD of Differnce Models    ########
#####                                                   ########
#####                                                   ########
################################################################


import rasterio as rio
import rasterio.mask
from rasterio.plot import show

import glob

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm

import Config

def DODSubPlot():
    """
    Creates one single subplot figure of all Digital Elevation Models of
    Difference.

    Returns
    -------
    Png subplot a combined subplot of elevation of difference models.

    """
    multiple_rasters = [sorted(glob.glob(Config.path+'*DOD.tif'))]
    num = (len(sorted(glob.glob(Config.path+"*DOD.tif"))))
    nums = num -1
    print(num)
    if (num % 2) == 0:
        print('fine')
    else:
        num = num + 1
    
    plt.figure(figsize=(10,30))
    for i in multiple_rasters:
        for count in range(0,len(multiple_rasters[0])):
            # if count <= num:
                # print(i[count])
        ###use the counter to index the mask glob results list [0]
                print(count+1, i)
                older = rio.open(i[count])
                oldy = older.read(1)
                # masky = older.read_maskS(1)
                
                oldy = np.ma.array(oldy, mask = (oldy == -9999.0))
                print(oldy.min(), oldy.max())

                ax = plt.subplot(num,2,count+1)
                
                norm = matplotlib.colors.TwoSlopeNorm(vmin = oldy.min(), vcenter = 0, vmax= oldy.max())
                show((oldy), ax=ax, cmap='seismic_r',vmin = oldy.min(),vmax = oldy.max(),norm = norm, transform = older.transform, title = 'DOD %s - %s' %(i[count][-19:-13],i[count][-13:-7]))
                cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                cbar.ax.tick_params(labelsize = 8)
                plt.tight_layout()
                plt.xticks(size=7)
                plt.yticks(size=7)      
                plt.savefig(Config.save_to_path+'/'+'DOD Subplots.png')