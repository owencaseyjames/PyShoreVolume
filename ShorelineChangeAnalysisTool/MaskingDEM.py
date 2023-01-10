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
from rasterio.plot import show , show_hist

import glob

import fiona
# import rioxarray

import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
import pandas as pd

import os 
import scipy
from scipy.spatial.distance import cdist, pdist

import numpy as np

import shapely
from shapely.geometry import Point, MultiPoint, box
from shapely.ops import nearest_points

import sklearn
from sklearn import preprocessing

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

import contextily as ctx

import time

import datetime
from datetime import datetime

import Config


def masking():
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
        out_meta.update({'driver':'GTiff', 'height':out_image.shape[1],'width':out_image.shape[2],'transform':out_transform})    
        with rio.open(Config.path+date+'masked.tif','w', **out_meta) as dest:
              dest.crs = rasterio.crs.CRS.from_epsg(27700)
              dest.write(out_image)          
        lidardem = rio.open(Config.path+date+'masked.tif')
        plt.imshow(lidardem.read(1) , cmap='pink')


