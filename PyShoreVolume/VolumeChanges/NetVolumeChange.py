#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 11:59:38 2023

@author: owenjames
"""
#NetVolumeChange.py

################################################################
##########             Net Volume Change           #############
##### Net Volume Chnages between Oldest and Newest.     ########
#####                                                   ########
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


######NET VOLUME CHANGE CAN JUST CALL UP THE OLDEST AND NEWSEST DOD FILE AND APPLY
#### THE VOLUMETRIC TRANSFORMATION FROM THE CONFIG PIXEL SETTING ON IT. 
def NetVolumeChange(path, pixelsize, measurementerror):
            """ 
            Applies the pixel size parameter to the elevation models to calculate 
            volumetric changes between oldest and newest dates. 
        
            Returns
            -------
            Volumetric changes within and outside of limits of detection
        
            """
            num = (len(sorted(glob.glob(path+"*masked.tif")))-1)
            maskglobresults = [sorted(glob.glob(path+"*masked.tif"))]
            older = rio.open(maskglobresults[0][0])
            newer = rio.open(maskglobresults[0][num])
            date1 = (maskglobresults[0][0][-16:-10])
            date2 = (maskglobresults[0][num][-16:-10])
            file = glob.glob(path+date1+date2+'DOD.tif')
            volfile = rio.open(file[0])
            readvolfile = np.array(volfile.read(1))
            readvolfile = np.ma.masked_where(readvolfile == -9999, readvolfile)
            
            vols = readvolfile * pixelsize
            
            ##Volume Stats !!! Positive means accretion, negative erosion!!! 
            print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
             
            ###Volume Limit of detection error may end up showing larger erosion or accretion by removing any pixels outside of the detection range)
            lods = np.ma.masked_where((-abs(measurementerror) < vols) & (vols < measurementerror), vols)
            
            print("\nThe total volume of change including Limit of Detection is \n", np.sum(lods), "\n(m3)\n")
            netchange = {}
            netchange[date1+'-'+date2] = {'Volume':np.sum(vols),'LODVols': np.sum(lods)}
            netvols = pd.DataFrame(netchange)
            netvols = netvols.T
            return netvols 

