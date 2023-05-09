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

def OldesttoNewest(path, save_to_path, DODCRS):    
            """
            Creates a DEM of difference between the oldest DEM and Newest DEM. Allows 
            DEM's of different sizes within the calculation by cropping the larger 
            DEM to the size of the smaller then performing the calculation.
            
        
            Returns
            -------
            Digital Elevation Model of Difference with graphical production.
        
            """
            num = (len(sorted(glob.glob(path+"*masked.tif")))-1)
            # print(num)
            maskglobresults = [sorted(glob.glob(path+"*masked.tif"))]

            older = rio.open(maskglobresults[0][0])
            newer = rio.open(maskglobresults[0][num])
            date1 = (maskglobresults[0][0][-16:-10])
            date2 = (maskglobresults[0][num][-16:-10])
            #           ##Create empty array of shape of newer raster
                  
            new= newer.read(1, masked = True)
            old= older.read(1, masked = True)
            

            if new.shape == old.shape: 
                    x = np.empty(newer.read(1).shape, dtype = rasterio.float32)
    
                    
                    imagenewmask = np.ma.array(new, mask = ((new == -9999.0)|(new == 0.0)))
                    imageoldmask = np.ma.array(old, mask = ((old == -9999.0)|(old == 0.0)))
                    
                    mask1 = np.ma.getmask(imagenewmask)
                    mask2 = np.ma.getmask(imageoldmask)
                
                    mask = np.logical_or(mask1,mask2)
                    
                    x = np.where(((imagenewmask != 0.0)&(imageoldmask != 0.0)), imagenewmask - imageoldmask, x)
                    x = np.ma.array(x, mask = (mask))
                    
                    out_meta = newer.meta
                    with rio.open(path+date1+date2+'DOD.tif','w',**out_meta) as dest:
                          dest.write(x.filled(fill_value = -9999.0), 1)

                    lidardem = rio.open(path+date1+date2+'DOD.tif')
                    lidardem1 = np.array(lidardem.read(1))
                    
                    lidardem1 = np.ma.array(lidardem1, mask=(mask))
                    
                    
                    fig, ax = plt.subplots(1, figsize=(5,5)) 
                    
                         
                    norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))

                    show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform, \
                         title = 'DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]))
                    cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                    plt.xticks(size = 5)
                    plt.yticks(size = 5)
                    plt.show()
                    fig.savefig(save_to_path+'/NetHeightChange.png')
                    show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                

            elif new.shape < old.shape:
                  ## Use the bounding box of the newer raster - making shapefile to clip by
                 
                  boundbox  = newer.bounds
                  geom = box(*boundbox)
                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                    ###Shapefile
                  df.to_file(path+'boundary.shp')
                  with fiona.open(path+'boundary.shp','r') as shapefile:
                      shapes = [feature['geometry'] for feature in shapefile]

                    ###Clip older mask by newer shapefile
                  
                  out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True, nodata = -9999)
                  out_meta = older.meta
                  out_meta.update({'driver':'GTiff','count':1, 'height':newer.shape[0],'width':newer.shape[1],'transform':out_transform})
                    
                  with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                          dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                          dest.write(out_image)
                  olderimage = rio.open(path+date1+date2+'bounding.tif')
                  old= olderimage.read(1, masked = True)
                  
                  
                  imagenewmask = np.ma.array(new, mask = ((new == -9999.0)|(new == 0.0)))
                  imageoldmask = np.ma.array(old, mask = ((old == -9999.0)|(old == 0.0)))
                    
                  mask1 = np.ma.getmask(imagenewmask)
                  mask2 = np.ma.getmask(imageoldmask)
                
                  mask = np.logical_or(mask1,mask2)
                  
                  x = np.empty(newer.read(1).shape, dtype = rasterio.float32)                  
                  x = np.where(((imagenewmask != 0.0)&(imageoldmask != 0.0)), imagenewmask - imageoldmask, x)               
                  x = np.ma.array(x, mask = (mask))
                  
                  
                  out_meta = newer.meta
                  with rio.open(path+date1+date2+'DOD.tif','w',**out_meta) as dest:
                          dest.write(x.filled(fill_value = -9999.0), 1)
                    # x = np.ma.array(x, mask=(mask))
                    
                  lidardem = rio.open(path+date1+date2+'DOD.tif')
                  lidardem1 = np.array(lidardem.read(1))
                    # print(lidardem1.max())
                  lidardem1 = np.ma.array(lidardem1, mask=(mask))
                    
                    
                  fig, ax = plt.subplots(1, figsize=(5,5)) 
              
                  norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                  show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform, \
                       title = 'DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]))
                  cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                  plt.xticks(size = 5)
                  plt.yticks(size = 5)
                  plt.show()
                  fig.savefig(save_to_path+'/NetChange.png')
                  show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                  

            elif new.shape > old.shape:    
                    ##Older bounding box shape
                  
                  boundbox  = older.bounds
                  geom = box(*boundbox)
                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                  
                  df.to_file(path+'boundary.shp')
                  with fiona.open(path+'boundary.shp','r') as shapefile:
                      shapes = [feature['geometry'] for feature in shapefile]
               
                    ##Clip newer raster
                  out_image, out_transform = rasterio.mask.mask(newer, shapes, crop=True, filled = True, nodata = -9999)
                  out_meta = older.meta
                  out_meta.update({'driver':'GTiff', 'count':1, 'height':older.shape[0],'width':older.shape[1],'transform':out_transform})
                    
                  with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                          dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                          dest.write(out_image)
                  newerimage = rio.open(path+date1+date2+'bounding.tif')
                  new= newerimage.read(1, masked = True)
                  
                  
                  imagenewmask = np.ma.array(new, mask = ((new == -9999.0)|(new == 0.0)))
                  imageoldmask = np.ma.array(old, mask = ((old == -9999.0)|(old == 0.0)))
                    
                  mask1 = np.ma.getmask(imagenewmask)
                  mask2 = np.ma.getmask(imageoldmask)
                
                  mask = np.logical_or(mask1,mask2)
                  
                  mask = np.logical_or(mask1,mask2)
                  
                  x = np.empty(newer.read(1).shape, dtype = rasterio.float32)                  
                  x = np.where(((imagenewmask != 0.0)&(imageoldmask != 0.0)), imagenewmask - imageoldmask, x)               
                  x = np.ma.array(x, mask = (mask))
                  
                  
                  out_meta = newer.meta
                  with rio.open(path+date1+date2+'DOD.tif','w',**out_meta) as dest:
                          dest.write(x.filled(fill_value = -9999.0), 1)
     
                  lidardem = rio.open(path+date1+date2+'DOD.tif')
                  lidardem1 = np.array(lidardem.read(1))
       
                  lidardem1 = np.ma.array(lidardem1, mask=(mask))
                    
                    
                  fig, ax = plt.subplots(1, figsize=(5,5)) 
              
                  norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                  show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform, \
                       title = 'DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]))
                  cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                  plt.xticks(size = 5)
                  plt.yticks(size = 5)
                  plt.show()
                  fig.savefig(save_to_path+'/NetHeightChange.png')
                  show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                  

             
            
            
            
            
            