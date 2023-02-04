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
        """
        Identifies the masked DEM's in directory and iterates through them performing
        Elevation models of difference. Allows DEM's of different sizes within the 
        calculation by cropping the larger DEM to the size of the smaller then 
        performing the calculation.
        
    
        Returns
        -------
        Series of elevation dfference models along with model difference graphs. 
    
        """
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


                    date1 = (i[count][-16:-10])
                    date2 = (i[count+1][-16:-10])

                    new = np.array(newer.read(1),dtype = rasterio.float32)             
                    old = np.array(older.read(1),dtype = rasterio.float32)

            
                    if old.shape == new.shape: 
                        
                        ###MASK AND SUB FUNC
                    
                        x = np.empty(newer.read(1).shape, dtype = rasterio.float32)

                        imagenewmask = np.ma.array(new, mask = ((new == -9999.0)|(new == 0.0)))
                        imageoldmask = np.ma.array(old, mask = ((old == -9999.0)|(old == 0.0)))
                        
                        mask1 = np.ma.getmask(imagenewmask)
                        mask2 = np.ma.getmask(imageoldmask)
                    
                        mask = np.logical_or(mask1,mask2)

                        x = np.where(((imagenewmask != 0.0)&(imageoldmask != 0.0)), imagenewmask - imageoldmask, x)
                        # x  = np.subtract(imagenewmask,imageoldmask)   
                        x = np.ma.array(x, mask = (mask))
                        
                        out_meta = newer.meta
                        with rio.open(Config.path+date1+date2+'DOD.tif','w',**out_meta) as dest:
                              dest.write(x.filled(fill_value = -9999.0), 1)
                        # x = np.ma.array(x, mask=(mask))
                        
                        
                        ###PLOT FUNC
                        
                        lidardem = rio.open(Config.path+date1+date2+'DOD.tif')
                        lidardem1 = np.array(lidardem.read(1))
                        # print(lidardem1.max())
                        lidardem1 = np.ma.array(lidardem1, mask=(mask))
                        
                        
                        fig, ax = plt.subplots(1, figsize=(5,5)) 
                  
                        norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
                        show((lidardem1) , ax = ax, cmap='seismic_r',vmin = lidardem1.min(),vmax = lidardem1.max(),norm = norm, transform = lidardem.transform, title = 'DOD %s - %s' %(date1 , date2))
                        cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                        plt.xticks(size = 5)
                        plt.yticks(size = 5)
                        plt.show()
                        fig.savefig(Config.save_to_path+'/'+date1+date2+'DOD.png')
                        # x = np.subtract(imagenewmask, imageoldmask)
                    elif new.shape < old.shape:
                          print('elif 1')
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
                          out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True,  nodata = -9999.0)
                          out_meta = newer.meta

                          out_meta.update({'driver':'GTiff', 'height':newer.shape[0],'width':newer.shape[1],'transform':out_transform})
                          ###maybe change height according to new shape and old shape.
                            
                          with rio.open(Config.path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                  dest.crs = rasterio.crs.CRS.from_epsg(27700)
                                  dest.write(out_image)
                          olderimage = rio.open(Config.path+date1+date2+'bounding.tif')

                          old = np.array(olderimage.read(1),dtype = rasterio.float32)
                          
                          
                          
                          imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                          imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))
                          # imagenewmask = np.ma.masked_where((new == 0.0)&(new == -9999.0), new)
                       
                          imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                          imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))

                          
                          mask1 = np.ma.getmask(imagenewmask)
                          mask2 = np.ma.getmask(imageoldmask)
                    
                          mask = np.logical_or(mask1,mask2)
                          
                          x = np.empty(newer.read(1).shape, dtype = rasterio.float32)

                          x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                          x = np.ma.array(x, mask = (mask))
                          with rio.open(Config.path+date1+date2+'DOD.tif','w',**out_meta) as dest:
                              dest.write(x.filled(fill_value = -9999.0), 1)
                              
                          lidardem = rio.open(Config.path+date1+date2+'DOD.tif')
                          
                          lidardem1 = np.array(lidardem.read(1))
     
                          lidardem1 = np.ma.array(lidardem1, mask=(mask))
                          fig, ax = plt.subplots(1, figsize=(5,5)) 
                          
                          
                          norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
                          show((lidardem1) , ax = ax, cmap='seismic_r',vmin = lidardem1.min(),vmax = lidardem1.max(),norm = norm, transform = lidardem.transform, title = 'DOD %s - %s' %(date1 , date2))
                          cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                          plt.xticks(size = 5)
                          plt.yticks(size = 5)
                          plt.show()
                          fig.savefig(Config.save_to_path+'/'+date1+date2+'DOD.png')    

                            ##if newer shape is bigger than the older shape 
                    elif new.shape > old.shape:   
                        
                         
                        
                          print('elif2')
                            ##Older bounding box shape
                          x = np.empty(older.read(1).shape, dtype = rasterio.float32)
                          
                          boundbox  = older.bounds
                          geom = box(*boundbox)
                          df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                          df = df.set_crs(27700)
                          df.to_file(Config.path+'boundary.shp')
                          with fiona.open(Config.path+'boundary.shp','r') as shapefile:
                              shapes = [feature['geometry'] for feature in shapefile]
                              

                          out_image, out_transform = rasterio.mask.mask(newer, shapes, crop=True, filled = True, nodata = -9999.0)
                          
                          out_meta = older.meta

                          out_meta.update({'driver':'GTiff', 'height':older.shape[0],'width':older.shape[1],'transform':out_transform})
                       
                          with rio.open(Config.path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                  dest.crs = rasterio.crs.CRS.from_epsg(27700)
                                  dest.write(out_image)
                                  
                          newerimage = rio.open(Config.path+date1+date2+'bounding.tif')
                          
                          new = np.array(newerimage.read(1),dtype = rasterio.float32)
                          
                          imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                          imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))

                          imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                          imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))

                          # imageoldmask = np.ma.masked_where((old  == 0.0)&(old == -9999.0), old)
                          mask1 = np.ma.getmask(imagenewmask)
                          mask2 = np.ma.getmask(imageoldmask)
                    
                          mask = np.logical_or(mask1,mask2)

                          x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)

                          x = np.ma.array(x, mask = (mask))

                          with rio.open(Config.path+date1+date2+'DOD.tif','w',**out_meta) as dest:
                              dest.write(x.filled(fill_value = -9999.0), 1)    
                          
                          lidardem = rio.open(Config.path+date1+date2+'DOD.tif')
                          
                          
                          lidardem1 = np.array(lidardem.read(1))
                          masky = lidardem.read_masks(1)

                          lidardem1 = np.ma.array(lidardem1, mask=(mask))
                          # print(lidardem1[2600,2600])
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