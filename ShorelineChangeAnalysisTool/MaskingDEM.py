#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 09:33:45 2023

@author: owenjames
"""

# MaskingofDEM.py

################################################################
##########               Mask all DEMS             #############
##### Masks all the DEMs using shapefile produced in    ########
##### preprocessing.                                    ########
#####                                                   ########
################################################################

import rasterio as rio
import rasterio.mask

import glob

import fiona

import Config

def masking():
    """
    Crops the DEM's using prior made vector shapefile and masks regions outside
    of the desired area.

    Returns
    -------
    Masked DEM's to be saved in the chosen directory. 

    """
    with fiona.open(Config.path+'Volumepoly.shp','r') as shapefile:
        shapes = [feature['geometry'] for feature in shapefile]
    globresults = glob.glob(Config.path+"*.tif")
    print(sorted(globresults))
    for i in sorted(globresults):
        file = rio.open(i)
        date = (i[-10:-4])
    ###Apply mask and crop using shapefile
        out_image, out_transform = rasterio.mask.mask(file, shapes, crop=True, filled = True, nodata = -9999.0)
        out_meta = file.meta
        
        out_meta.update({'driver':'GTiff', 'crs':'EPSG:27700','height':out_image.shape[1],'width':out_image.shape[2],'transform':out_transform, 'nodata':-9999.0})    
        with rio.open(Config.path+date+'masked.tif','w', **out_meta) as dest:
              dest.crs = rasterio.crs.CRS.from_epsg(27700)
              dest.write(out_image)          
        lidardem = rio.open(Config.path+date+'masked.tif')
        plt.imshow(lidardem.read(1) , cmap='pink')


