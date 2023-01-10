#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 10:08:05 2023

@author: owenjames
"""
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


################################################################
########## Digital Elelevation Model of Difference #############
#####This model subtracts the newer DEM from the elder, ########
#####producing net volume change DEM that can be used   ########
#####used to assess volumetric change.                  ########
################################################################

def DEMofDifference():
     
        maskglobresults = [sorted(glob.glob(Config.path+"*masked.tif"))]
        num = (len(sorted(glob.glob(Config.path+"*masked.tif")))-1)
        print(num)
        for i in maskglobresults:
            for count in range(0,len(maskglobresults[0])):
        ###use the counter to index the mask glob results list [0]
                if count < num:
                    print(count)
                    older = rio.open(i[count])
                    newer = rio.open(i[count+1])
                
                      ##Get the dates for naming of files
                    date1 = (i[count][-16:-10])
                    date2 = (i[count+1][-16:-10])
            
                      ##Create empty array of shape of newer raster
                    x = np.empty(newer.read(1).shape, dtype = rasterio.float32)
                    
                    new= np.array(newer.read(1, masked = True))
                    imagenewmask = np.ma.masked_where(new == -9999.0, new)
                    old= np.array(older.read(1, masked = True))
                    imageoldmask = np.ma.masked_where(old == -9999.0, old)
                    print(new.shape, old.shape)
                    print(new, old)
                    print(imagenewmask, imageoldmask)
                    print(date1,date2)
                      ##Create a polygon out of the bounding box of the smaller polygon - clip the older one to this then
                      ###perform the subtraction. 
            
                    if imagenewmask.shape == imageoldmask.shape: 
                        x = np.where(imagenewmask, imagenewmask - imageoldmask, x)
                    elif imagenewmask.shape < imageoldmask.shape:
                          ## Use the bounding box of the newer raster - making shapefile to clip by
                          boundbox  = newer.bounds
                          geom = box(*boundbox)
                          df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                          df = df.set_crs(27700)
                          #   ###Shapefile
                          df.to_file(Config.path+'boundary.shp')
                          with fiona.open(Config.path+'boundary.shp','r') as shapefile:
                               shapes = [feature['geometry'] for feature in shapefile]
                        #     file = rio.open(i)
                        #     date = (i[-10:-4])
                            ###Clip older mask by newer shapefile
                          out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True, all_touched = False, nodata = -9999)
                          out_meta = older.meta
                          print(out_image.shape[1]-1,out_image.shape[2])
                          out_meta.update({'driver':'GTiff', 'height':out_image.shape[1] - 1,'width':out_image.shape[2],'transform':out_transform})
                          ###maybe change height according to new shape and old shape.
                            
                          with rio.open(Config.path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                  dest.crs = rasterio.crs.CRS.from_epsg(27700)
                                  dest.write(out_image)
                          olderimage = rio.open(Config.path+date1+date2+'bounding.tif')
                          plt.figure(figsize=(5,5))    
                          show((olderimage,1) , cmap='seismic',vmin = -8,vmax= 8, transform = lidardem.transform)
                          plt.show()
                          old = np.array(olderimage.read(1, masked = True))
                          
                          imageoldmask = np.ma.masked_where(old == -9999.0, old)
                          print(imageoldmask)
                          
                          x = np.where(imagenewmask, imagenewmask - imageoldmask, x)
                          # x = np.subtract(new, old, where = new > -9999)
                          x = np.ma.masked_where(x == -9999.0, x, copy = True)
                          print(x[2000,1200], x[0,0])
                          # x = np.ma.masked_where(xi > 9999.0, xi)
                          print(x[2000,1200])
                            ##if newer shape is bigger than the older shape 
                    elif imagenewmask.shape > imageoldmask.shape:    
                            ##Older bounding box shape
                          print(older.bounds)
                          boundbox  = older.bounds
                          geom = box(*boundbox)
                          df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                          df = df.to_crs(27700)
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
                          # x = np.subtract(new, old, where = new > -9999)
                          xmask = np.ma.masked_array(x, mask=(x == -9999))
                          print(x, xmask)
                    
            
                    ###TO TIFF
                    print(newer.meta)
                    
                    out_meta = newer.meta  
                    out_meta.update({'crs':'EPSG:27700', 'transform':newer.transform,})
                    # print(out_meta)
                    with rio.open(Config.path+date1+date2+'DOD.tif','w',**out_meta) as dest:
                          dest.write(x, 1)          
                    
                    
                    lidardem = rio.open(Config.path+date1+date2+'DOD.tif')
                    print(lidardem.transform)
                    lidardem1 = np.ma.masked_where(lidardem.read(1) == -9999.0, lidardem.read(1), copy =True)
                    fig, ax = plt.subplots(1, figsize=(5,5)) 
                    
                    norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
                    show((lidardem1) , ax = ax, cmap='seismic_r',vmin = lidardem1.min(),vmax = lidardem1.max(),norm = norm, transform = lidardem.transform, title = 'DOD %s - %s' %(date1 , date2))
                    cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                    plt.xticks(size = 5)
                    plt.yticks(size = 5)
                    plt.show()
                    fig.savefig(Config.save_to_path+'/'+date1+date2+'DOD.png')
            else:
                break
    # except I
    # ndexError:
    #     pass