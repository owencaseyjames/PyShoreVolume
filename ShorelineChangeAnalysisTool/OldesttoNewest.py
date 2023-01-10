#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 12:14:25 2023

@author: owenjames
"""
################################################################
##########           Oldest to Newest DOD          #############
#####DOD of the Oldest DEM to Newest DEM showing net    ########
#####change.                                            ########
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


def OldesttoNewestDOD():    
            num = (len(sorted(glob.glob(Config.path+"*masked.tif")))-1)
            print(num)
            maskglobresults = [sorted(glob.glob(Config.path+"*masked.tif"))]
            print(len(maskglobresults[:])) 
            older = rio.open(maskglobresults[0][0])
            newer = rio.open(maskglobresults[0][num])
            date1 = (maskglobresults[0][0][-16:-10])
            date2 = (maskglobresults[0][num][-16:-10])
            #           ##Create empty array of shape of newer raster
            x = np.empty(newer.read(1).shape, dtype = rasterio.float32)
                    
            new= newer.read(1, masked = True)
            # new = new #* 0.01
            imagenewmask = np.ma.masked_where(new == -9999, new)
            old= older.read(1, masked = True)
            # old = old #* 0.01
            imageoldmask = np.ma.masked_where(old == -9999, old)
            print(imageoldmask)
            if imagenewmask.shape == imageoldmask.shape: 
                x = np.where(imagenewmask, imagenewmask - imageoldmask, x)
                # x = np.subtract(new, old, where = new > -9999)
                xmask = np.ma.masked_array(x, mask=(x == -9999))
            elif imagenewmask.shape < imageoldmask.shape:
                  ## Use the bounding box of the newer raster - making shapefile to clip by
                  boundbox  = newer.bounds
                  geom = box(*boundbox)
                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                    ###Shapefile
                  df.to_file(Config.path+'boundary.shp')
                  with fiona.open(Config.path+'boundary.shp','r') as shapefile:
                      shapes = [feature['geometry'] for feature in shapefile]
                #     file = rio.open(i)
                #     date = (i[-10:-4])
                    ###Clip older mask by newer shapefile
                  
                  out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True, nodata = -9999)
                  out_meta = older.meta
                  out_meta.update({'driver':'GTiff', 'height':out_image.shape[1]-1,'width':out_image.shape[2],'transform':out_transform})
                    
                  with rio.open(Config.path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                          dest.crs = rasterio.crs.CRS.from_epsg(27700)
                          dest.write(out_image)
                  olderimage = rio.open(Config.path+date1+date2+'bounding.tif')
                  old= olderimage.read(1, masked = True)
                  imageoldmask = np.ma.masked_where(old == -9999, old)
            
                  x = np.where(imagenewmask, imagenewmask - imageoldmask, x)
                  # x = np.subtract(new, old, where = new > -9999)
                  xmask = np.ma.masked_array(x, mask=(x == -9999))
                    ##if newer shape is bigger than the older shape 
            elif imagenewmask.shape > imageoldmask.shape:    
                    ##Older bounding box shape
                  print(older.bounds)
                  boundbox  = older.bounds
                  geom = box(*boundbox)
                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                  
                  df.to_file(Config.path+'boundary.shp')
                  with fiona.open(Config.path+'boundary.shp','r') as shapefile:
                      shapes = [feature['geometry'] for feature in shapefile]
                #     file = rio.open(i)
                #     date = (i[-10:-4])
                    ##Clip newer raster
                  out_image, out_transform = rasterio.mask.mask(newer, shapes, crop=True, filled = True, nodata = -9999)
                  out_meta = older.meta
                  out_meta.update({'driver':'GTiff', 'height':out_image.shape[1],'width':out_image.shape[2],'transform':out_transform})
                    
                  with rio.open(Config.path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                          dest.crs = rasterio.crs.CRS.from_epsg(27700)
                          dest.write(out_image)
                  newerimage = rio.open(Config.path+date1+date2+'bounding.tif')
                  new= newerimage.read(1, masked = True)
                  imagenewmask = np.ma.masked_where(new == -9999, new)
                  # print(imagenewmask)  
                  x = np.where(imagenewmask, imagenewmask - imageoldmask, x)
                  # x = np.subtract(new, old, where = new >-9999)
                  xmask = np.ma.masked_array(x, mask=(x == -9999))
                  print(xmask)
             
            # ##TO TIFF
            
            out_meta = newer.meta  
            out_meta.update({'crs':'EPSG:4326', 'transform':newer.transform,})
            # print(out_meta)
            with rio.open(Config.path+date1+date2+'DOD.tif','w',**out_meta) as dest:
                  dest.write(x,1)          
            lidardem = rio.open(Config.path+date1+date2+'DOD.tif')
            lidardem1 = lidardem.read(1)
            lidardem1 = np.ma.masked_where(lidardem.read(1) == -9999.0, lidardem.read(1), copy =True)
            # lidardem1 = np.ma.masked_array(lidardem1, mask=(lidardem1 == -9999))
            print(lidardem1)
            fig, ax = plt.subplots(1, figsize=(5,5)) 
            norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
            show((lidardem1) , ax = ax, cmap='seismic_r',vmin = lidardem1.min(),vmax = lidardem1.max(),norm = norm, transform = lidardem.transform, title = '2007/02 - 2020/09 Net Height Change')
            cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
            plt.xticks(size = 5)
            plt.yticks(size = 5)
            plt.show()
            plt.savefig(Config.save_to_path+'/NetHeightChange.png')
            # fig.savefig(save_to_path+'/'+date1+date2+'DOD.png')
            totals = np.sum(lidardem1)
            # print('The total  nm2totals)
            show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)