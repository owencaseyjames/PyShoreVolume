#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 10:26:19 2023

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

import re

import pickle

################################################################
########## Digital Elelevation Model of Difference #############
#####This model subtracts the newer DEM from the elder, ########
#####producing net volume change DEM that can be used   ########
#####used to assess volumetric change.                  ########
################################################################

#%%
def autumnDOD(path, pixelsize, save_to_path, DODCRS): 
                """
                Identifies the masked DEM's in directory and iterates through them performing
                Elevation models of difference. Allows DEM's of different sizes within the 
                calculation by cropping the larger DEM to the size of the smaller then 
                performing the calculation.
                
                
                Returns
                -------
                Series of elevation dfference models along with model difference graphs. 
                """
                maskglobresults = [sorted(glob.glob(path+"*masked.tif"))]
                num = (len(sorted(glob.glob(path+"*masked.tif")))-1) 
                seasonfile = []
                for i in maskglobresults[0]:
                    if re.search('[0-9][0-9][0-9][0-9][0-0][9-9]masked.tif',i):
                        seasonfile.append(i)
                    elif re.search('[0-9][0-9][0-9][0-9][1-1][0-1]masked.tif',i):
                        seasonfile.append(i)                    
                    else:
                        continue
                   
                num = (len(seasonfile)-1)
                autumndic = {}
                for e, i in enumerate(seasonfile):
                ###use the counter to index the mask glob results list [0]
                        if e < num:
                            
                            older = rio.open(i)
                            newer = rio.open(seasonfile[seasonfile.index(i)- len(seasonfile)+1])
                
                
                            date1 = (i[-16:-10])
                            date2 = (seasonfile[seasonfile.index(i)- len(seasonfile)+1][-16:-10])
                            
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

                                x = np.ma.array(x, mask = (mask))
                                
                                out_meta = newer.meta
                                with rio.open(path+date1+date2+'autumn.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1)
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)

                                ###PLOT FUNC
                                
                                lidardem = rio.open(path+date1+date2+'autumn.tif')
                                lidardem1 = np.array(lidardem.read(1))
                             
                                lidardem1 = np.ma.array(lidardem1, mask=(mask))
                                
  
                                #Plot
                                fig = matplotlib.pyplot.figure()
                                ax = fig.add_subplot(1,1,1)

                                norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                                
                                show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform)
                                
                                ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)
                                cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                cbar.set_label('Elevation Change (m)',rotation=270, labelpad=10)
                                plt.tight_layout()
                                plt.xticks(size = 5)
                                plt.yticks(size = 5)
                                plt.show()
                                show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                fig.savefig(save_to_path+'/'+date1+date2+'autumn.png',bbox_inches='tight')
                                
                                #Volume
                                vols = lidardem1 * pixelsize
                                print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")

     
                            elif new.shape < old.shape:
                                 
                                  ## Use the bounding box of the newer raster - making shapefile to clip by
                                  
                                  boundbox  = newer.bounds
                                  geom = box(*boundbox)
                                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                                 
                                  #   ###Shapefile
                                  df.to_file(path+'boundary.shp')
                                  with fiona.open(path+'boundary.shp','r') as shapefile:
                                        shapes = [feature['geometry'] for feature in shapefile]

                                    ###Clip older mask by newer shapefile
                                  out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True,  nodata = -9999.0)
                                  out_meta = newer.meta
                
                                  out_meta.update({'driver':'GTiff', 'count':1,'height':newer.shape[0],'width':newer.shape[1],'transform':out_transform})
                                  ###maybe change height according to new shape and old shape.
                                    
                                  with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                          dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                          dest.write(out_image)
                                  olderimage = rio.open(path+date1+date2+'bounding.tif')
                
                                  old = np.array(olderimage.read(1),dtype = rasterio.float32)
                                  
                                  
                                  
                                  imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                                  imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))

                               
                                  imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                                  imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
                
                                  
                                  mask1 = np.ma.getmask(imagenewmask)
                                  mask2 = np.ma.getmask(imageoldmask)
                            
                                  mask = np.logical_or(mask1,mask2)
                                  
                                  x = np.empty(newer.read(1).shape, dtype = rasterio.float32)
                
                                  x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                                  x = np.ma.array(x, mask = (mask))
                                  with rio.open(path+date1+date2+'autumn.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1)
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                      
                                  lidardem = rio.open(path+date1+date2+'autumn.tif')
                                  lidardem1 = np.array(lidardem.read(1))
                                  lidardem1 = np.ma.array(lidardem1, mask=(mask))
                                  
                                  
                                  #Plot
                                  fig = matplotlib.pyplot.figure()
                                  ax = fig.add_subplot(1,1,1)
                                  

                                  norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                                  show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,)
                                  ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)

                                  cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                  cbar.set_label('Elevation Change (m)',rotation=270)
                                  plt.xticks(size = 5)
                                  plt.yticks(size = 5)
                                  plt.tight_layout()  
                                  plt.show()
                                  show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                  fig.savefig(save_to_path+'/'+date1+date2+'autumn.png',bbox_inches='tight') 
                                  
                                  #Volumes
                                  vols = lidardem1 * pixelsize
                                  print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")

                            elif new.shape > old.shape:   
     
                                  print('elif2')
                                    ##Older bounding box shape
                                  x = np.empty(older.read(1).shape, dtype = rasterio.float32)
                                  
                                  boundbox  = older.bounds
                                  geom = box(*boundbox)
                                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                                  # df = df.set_crs(DODCRS)
                                  df.to_file(path+'boundary.shp')
                                  with fiona.open(path+'boundary.shp','r') as shapefile:
                                      shapes = [feature['geometry'] for feature in shapefile]
                                      
                
                                  out_image, out_transform = rasterio.mask.mask(newer, shapes, crop=True, filled = True, nodata = -9999.0)
                                  
                                  out_meta = older.meta
                
                                  out_meta.update({'driver':'GTiff','count':1, 'height':older.shape[0],'width':older.shape[1],'transform':out_transform})
                               
                                  with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                          dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                          dest.write(out_image)
                                          
                                  newerimage = rio.open(path+date1+date2+'bounding.tif')
                                  
                                  new = np.array(newerimage.read(1),dtype = rasterio.float32)
                                  
                                  imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                                  imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))
                
                                  imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                                  imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
                
                              
                                  mask1 = np.ma.getmask(imagenewmask)
                                  mask2 = np.ma.getmask(imageoldmask)
                            
                                  mask = np.logical_or(mask1,mask2)
                
                                  x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                
                                  x = np.ma.array(x, mask = (mask))
                
                                  with rio.open(path+date1+date2+'autumn.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1)    
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                  
                                  lidardem = rio.open(path+date1+date2+'autumn.tif') 
                                  lidardem1 = np.array(lidardem.read(1))        
                                  lidardem1 = np.ma.array(lidardem1, mask=(mask))
                                 
                                  
                                  fig = matplotlib.pyplot.figure()
                                  ax = fig.add_subplot(1,1,1) 
                                
                            
                                  norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()) )                        
                                  show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,) 
                                       
                                  ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)    
                                  cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                  cbar.set_label('Elevation Change (m)', rotation=270)
                                  plt.tight_layout()
                                  plt.xticks(size = 5)
                                  plt.yticks(size = 5)
                                  plt.show()
                                  show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                  fig.savefig(save_to_path+'/'+date1+date2+'autumn.png',bbox_inches='tight')   
                                  
                                  #Volume
                                  vols = lidardem1 * pixelsize
                                  print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
                
                                  
                            autumndic[date1+'-'+date2] = {'Volumes': np.sum(vols), 'Date':['%s - %s' %(date1[4:7]+'/'+date1[0:4], date2[4:7]+'/'+date2[0:4])]}
                        else:
                                break    
                with open (save_to_path+'/autumndic.pkl', 'wb') as fb:
                                    pickle.dump(autumndic, fb, protocol = pickle.HIGHEST_PROTOCOL)            
                DOD  = pd.DataFrame(autumndic)
                DOD = DOD.T
                
                return  DOD   




#%%%
def winterDOD(path, pixelsize, save_to_path, DODCRS): 
                """
                Identifies the masked DEM's in directory and iterates through them performing
                Elevation models of difference. Allows DEM's of different sizes within the 
                calculation by cropping the larger DEM to the size of the smaller then 
                performing the calculation.
                
                
                Returns
                -------
                Series of elevation dfference models along with model difference graphs. 
                """
                maskglobresults = [sorted(glob.glob(path+"*masked.tif"))]

                num = (len(sorted(glob.glob(path+"*masked.tif")))-1) 
                seasonfile = []
                for i in maskglobresults[0]:

                    if re.search('[0-9][0-9][0-9][0-9][0-1][1-2]masked.tif',i):
                        seasonfile.append(i)
                    else:
                        continue
                num = (len(seasonfile)-1)
                winterdic = {}
                for e, i in enumerate(seasonfile):
                ###use the counter to index the mask glob results list [0]
                        if e < num:
                            
                            older = rio.open(i)
                            newer = rio.open(seasonfile[seasonfile.index(i)- len(seasonfile)+1])
                
                
                            date1 = (i[-16:-10])
                            date2 = (seasonfile[seasonfile.index(i)- len(seasonfile)+1][-16:-10])
                
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
                                 
                                x = np.ma.array(x, mask = (mask))
                                
                                out_meta = newer.meta
                                with rio.open(path+date1+date2+'winter.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1)
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)     
                               
                                
                                
                                ###PLOT FUNC
                                
                                lidardem = rio.open(path+date1+date2+'winter.tif')
                                lidardem1 = np.array(lidardem.read(1))

                                lidardem1 = np.ma.array(lidardem1, mask=(mask))
                                
                                #Plot
                                fig = matplotlib.pyplot.figure()
                                ax = fig.add_subplot(1,1,1)
                          
                                norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                                show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,)
                                ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)  

                                cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                cbar.set_label('Elevation Change (m)',rotation=270, labelpad=10)
                                plt.tight_layout()
                                plt.xticks(size = 5)
                                plt.yticks(size = 5)
                                plt.show()
                                show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                fig.savefig(save_to_path+'/'+date1+date2+'winter.png',bbox_inches='tight')
                                
                                
                                #Volume
                                vols = lidardem1 * pixelsize
                                print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
 
                            elif new.shape < old.shape:
                                  print('elif 1')
                                  ## Use the bounding box of the newer raster - making shapefile to clip by
                                  
                                  boundbox  = newer.bounds
                                  geom = box(*boundbox)
                                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                                
                                  #   ###Shapefile
                                  df.to_file(path+'boundary.shp')
                                  with fiona.open(path+'boundary.shp','r') as shapefile:
                                        shapes = [feature['geometry'] for feature in shapefile]

                                  out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True,  nodata = -9999.0)
                                  out_meta = newer.meta
                
                                  out_meta.update({'driver':'GTiff', 'count':1,'height':newer.shape[0],'width':newer.shape[1],'transform':out_transform})
                                  ###maybe change height according to new shape and old shape.
                                    
                                  with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                          dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                          dest.write(out_image)
                                  olderimage = rio.open(path+date1+date2+'bounding.tif')
                
                                  old = np.array(olderimage.read(1),dtype = rasterio.float32)
                                  
                                  
                                  
                                  imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                                  imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))
                               
                                  imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                                  imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
                
                                  
                                  mask1 = np.ma.getmask(imagenewmask)
                                  mask2 = np.ma.getmask(imageoldmask)
                            
                                  mask = np.logical_or(mask1,mask2)
                                  
                                  x = np.empty(newer.read(1).shape, dtype = rasterio.float32)
                
                                  x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                                  x = np.ma.array(x, mask = (mask))
                                  with rio.open(path+date1+date2+'winter.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1)
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                      
                                  lidardem = rio.open(path+date1+date2+'winter.tif')
                                  lidardem1 = np.array(lidardem.read(1))
                                  lidardem1 = np.ma.array(lidardem1, mask=(mask))
                                  
                                  
                                  fig = matplotlib.pyplot.figure()
                                  ax = fig.add_subplot(1,1,1) 
                                  
                                  
                                  norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                                  show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,) 

                                  ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)     
                                  cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                  plt.xticks(size = 5)
                                  plt.yticks(size = 5)
                                  plt.tight_layout() 
                                  plt.show()
                                  show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                  fig.savefig(save_to_path+'/'+date1+date2+'winter.png', bbox_inches='tight')    
                                  
                                  #Volume
                                  vols = lidardem1 * pixelsize
                                  print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")

                            elif new.shape > old.shape:   

                                  
                                    ##Older bounding box shape
                                  x = np.empty(older.read(1).shape, dtype = rasterio.float32)
                                  
                                  boundbox  = older.bounds
                                  geom = box(*boundbox)
                                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                                  df = df.set_crs(DODCRS)
                                  df.to_file(path+'boundary.shp')
                                  with fiona.open(path+'boundary.shp','r') as shapefile:
                                      shapes = [feature['geometry'] for feature in shapefile]
                                      
                
                                  out_image, out_transform = rasterio.mask.mask(newer, shapes, crop=True, filled = True, nodata = -9999.0)
                                  
                                  out_meta = older.meta
                
                                  out_meta.update({'driver':'GTiff','count':1, 'height':older.shape[0],'width':older.shape[1],'transform':out_transform})
                               
                                  with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                          dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                          dest.write(out_image)
                                          
                                  newerimage = rio.open(path+date1+date2+'bounding.tif')
                                  
                                  new = np.array(newerimage.read(1),dtype = rasterio.float32)
                                  
                                  imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                                  imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))
                
                                  imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                                  imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
                
                                  
                                  mask1 = np.ma.getmask(imagenewmask)
                                  mask2 = np.ma.getmask(imageoldmask)
                            
                                  mask = np.logical_or(mask1,mask2)
                
                                  x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                
                                  x = np.ma.array(x, mask = (mask))
                
                                  with rio.open(path+date1+date2+'winter.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1)  
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                  
                                  lidardem = rio.open(path+date1+date2+'winter.tif')
                                  lidardem1 = np.array(lidardem.read(1))
                                  lidardem1 = np.ma.array(lidardem1, mask=(mask))

                                  
                                  fig = matplotlib.pyplot.figure()
                                  ax = fig.add_subplot(1,1,1) 
                                  
                                  
                                  norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                                  show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,) 

                                  ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)
                                  cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                  cbar.set_label('Elevation Change (m)', rotation=270)
                                  plt.tight_layout()
                                  plt.xticks(size = 5)
                                  plt.yticks(size = 5)
                                  plt.show()
                                  show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                  fig.savefig(save_to_path+'/'+date1+date2+'winter.png', bbox_inches='tight')
                                  
                                  #Volumes
                                  vols = lidardem1 * pixelsize
                                  print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
                            
                            winterdic[date1+'-'+date2] = {'Volumes': np.sum(vols), 'Date':['%s - %s' %(date1[4:7]+'/'+date1[0:4], date2[4:7]+'/'+date2[0:4])]} 
                        else:
                            break
                with open (save_to_path+'/winterdic.pkl', 'wb') as fb:
                                    pickle.dump(winterdic, fb, protocol = pickle.HIGHEST_PROTOCOL)
                DOD  = pd.DataFrame(winterdic)
                DODres = DOD.T
                return  DODres     
#%%
def springDOD(path, pixelsize, save_to_path, DODCRS):
        maskglobresults = [sorted(glob.glob(path+"*masked.tif"))]
        
        num = (len(sorted(glob.glob(path+"*masked.tif")))-1) 
        seasonfile = []
        for i in maskglobresults[0]:            
            if re.search('[0-9][0-9][0-9][0-9][0-0][3-5]masked.tif',i):
                seasonfile.append(i)
            else:
                continue
        num = (len(seasonfile)-1)
        Springdic = {}
        for e, i in enumerate(seasonfile):
        ###use the counter to index the mask glob results list [0]
                if e < num:
                    
                    older = rio.open(i)
                    newer = rio.open(seasonfile[seasonfile.index(i)- len(seasonfile)+1])
        
        
                    date1 = (i[-16:-10])
                    date2 = (seasonfile[seasonfile.index(i)- len(seasonfile)+1][-16:-10])
                    
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
                        x = np.ma.array(x, mask = (mask))
                        
                        out_meta = newer.meta
                        with rio.open(path+date1+date2+'spring.tif','w',**out_meta) as dest:
                              dest.write(x.filled(fill_value = -9999.0), 1)

                        ###PLOT FUNC
                        
                        lidardem = rio.open(path+date1+date2+'spring.tif')
                        lidardem1 = np.array(lidardem.read(1))

                        lidardem1 = np.ma.array(lidardem1, mask=(mask))

                        #Plot
                        fig = matplotlib.pyplot.figure()
                        ax = fig.add_subplot(1,1,1)
                        
                        norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                        show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform) 
                            
                        ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]), fontsize=10)
                        cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                        cbar.set_label('Elevation Change (m)',rotation=270, labelpad=10)
                        plt.tight_layout()
                        plt.xticks(size = 5)
                        plt.yticks(size = 5)
                        plt.show()
                        show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                        fig.savefig(save_to_path+'/'+date1+date2+'spring.png')
                        
                        #Volume
                        vols = lidardem1 * pixelsize
                        print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")


                    elif new.shape < old.shape:
                          print('elif 1')
                          ## Use the bounding box of the newer raster - making shapefile to clip by
                          
                          boundbox  = newer.bounds
                          geom = box(*boundbox)
                          df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                          
                          #   ###Shapefile
                          df.to_file(path+'boundary.shp')
                          with fiona.open(path+'boundary.shp','r') as shapefile:
                                shapes = [feature['geometry'] for feature in shapefile]

                            ###Clip older mask by newer shapefile
                          out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True,  nodata = -9999.0)
                          out_meta = newer.meta
        
                          out_meta.update({'driver':'GTiff', 'count':1,'height':newer.shape[0],'width':newer.shape[1],'transform':out_transform})
                          ###maybe change height according to new shape and old shape.
                            
                          with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                  dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                  dest.write(out_image)
                          olderimage = rio.open(path+date1+date2+'bounding.tif')
        
                          old = np.array(olderimage.read(1),dtype = rasterio.float32)
                          

                          imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                          imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))

                       
                          imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                          imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
        
                          
                          mask1 = np.ma.getmask(imagenewmask)
                          mask2 = np.ma.getmask(imageoldmask)
                    
                          mask = np.logical_or(mask1,mask2)
                          
                          x = np.empty(newer.read(1).shape, dtype = rasterio.float32)
        
                          x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                          x = np.ma.array(x, mask = (mask))
                          with rio.open(path+date1+date2+'spring.tif','w',**out_meta) as dest:
                              dest.write(x.filled(fill_value = -9999.0), 1)
                              dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                              
                          lidardem = rio.open(path+date1+date2+'spring.tif')
                          lidardem1 = np.array(lidardem.read(1))
                          lidardem1 = np.ma.array(lidardem1, mask=(mask))
                          
                          
                          #Plot
                          fig = matplotlib.pyplot.figure()
                          ax = fig.add_subplot(1,1,1)
                          
                          
                          
                          norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                          show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,)
                          ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)

                          cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                          cbar.set_label('Elevation Change (m)',rotation=270)
                          plt.xticks(size = 5)
                          plt.yticks(size = 5)
                          plt.tight_layout()  
                          plt.show()
                          show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                          fig.savefig(save_to_path+'/'+date1+date2+'spring.png') 
                          
                          #Volumes
                          vols = lidardem1 * pixelsize
                          print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")

                    elif new.shape > old.shape:   

                          print('elif2')
                            ##Older bounding box shape
                          x = np.empty(older.read(1).shape, dtype = rasterio.float32)
                          
                          boundbox  = older.bounds
                          geom = box(*boundbox)
                          df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                          # df = df.set_crs(DODCRS)
                          df.to_file(path+'boundary.shp')
                          with fiona.open(path+'boundary.shp','r') as shapefile:
                              shapes = [feature['geometry'] for feature in shapefile]
                              
        
                          out_image, out_transform = rasterio.mask.mask(newer, shapes, crop=True, filled = True, nodata = -9999.0)
                          
                          out_meta = older.meta
        
                          out_meta.update({'driver':'GTiff','count':1, 'height':older.shape[0],'width':older.shape[1],'transform':out_transform})
                       
                          with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                  dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                  dest.write(out_image)
                                  
                          newerimage = rio.open(path+date1+date2+'bounding.tif')
                          
                          new = np.array(newerimage.read(1),dtype = rasterio.float32)
                          
                          imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                          imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))
        
                          imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                          imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
        

                          mask1 = np.ma.getmask(imagenewmask)
                          mask2 = np.ma.getmask(imageoldmask)
                    
                          mask = np.logical_or(mask1,mask2)
        
                          x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
        
                          x = np.ma.array(x, mask = (mask))
        
                          with rio.open(path+date1+date2+'spring.tif','w',**out_meta) as dest:
                              dest.write(x.filled(fill_value = -9999.0), 1)    
                              dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                          
                          lidardem = rio.open(path+date1+date2+'spring.tif') 
                          lidardem1 = np.array(lidardem.read(1))        
                          lidardem1 = np.ma.array(lidardem1, mask=(mask))
                          
                          
                          fig = matplotlib.pyplot.figure()
                          ax = fig.add_subplot(1,1,1) 
                        
                    
                          norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()) )                        
                          show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,) 

                          ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)    
                          cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                          cbar.set_label('Elevation Change (m)', rotation=270)
                          plt.tight_layout()
                          plt.xticks(size = 5)
                          plt.yticks(size = 5)
                          plt.show()
                          show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                          fig.savefig(save_to_path+'/'+date1+date2+'spring.png')   
                          
                          #Volume
                          vols = lidardem1 * pixelsize
                          print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
        
                          
                    Springdic[date1+'-'+date2] = {'Volumes': np.sum(vols), 'Date':['%s - %s' %(date1[4:7]+'/'+date1[0:4], date2[4:7]+'/'+date2[0:4])]}
                else:
                        break    
        with open (save_to_path+'/Springdic.pkl', 'wb') as fb:
                            pickle.dump(Springdic, fb, protocol = pickle.HIGHEST_PROTOCOL)            
        DOD  = pd.DataFrame(Springdic)
        DOD = DOD.T
        
        return  DOD   

#%%
def summerDOD(path, pixelsize, save_to_path, DODCRS):
                maskglobresults = [sorted(glob.glob(path+"*masked.tif"))]
                
                num = (len(sorted(glob.glob(path+"*masked.tif")))-1) 
                seasonfile = []
                for i in maskglobresults[0]:

                    if re.search('[0-9][0-9][0-9][0-9][0-0][6-8]masked.tif',i):
                        seasonfile.append(i)
                    else:
                        continue
                
                num = (len(seasonfile)-1)
                summerdic = {}
                for e, i in enumerate(seasonfile):
                ###use the counter to index the mask glob results list [0]
                        if e < num:
                            
                            older = rio.open(i)
                            newer = rio.open(seasonfile[seasonfile.index(i)- len(seasonfile)+1])
                
                
                            date1 = (i[-16:-10])
                            date2 = (seasonfile[seasonfile.index(i)- len(seasonfile)+1][-16:-10])
                
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

                                x = np.ma.array(x, mask = (mask))
                                
                                out_meta = newer.meta
                                with rio.open(path+date1+date2+'summer.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1)
            
                                
                                ###PLOT FUNC
                                
                                lidardem = rio.open(path+date1+date2+'summer.tif')
                                lidardem1 = np.array(lidardem.read(1))
                                lidardem1 = np.ma.array(lidardem1, mask=(mask))
                                

                                fig = matplotlib.pyplot.figure()
                                ax = fig.add_subplot(1,1,1)
                          
                                norm = matplotlib.colors.TwoSlopeNorm(vmin = int(lidardem1.min()), vcenter = 0, vmax= int(lidardem1.max()))
                                show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,)
                                ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)     

                                cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                cbar.set_label('Elevation Change (m)',rotation=270, labelpad=10)
                                plt.tight_layout()
                                plt.xticks(size = 5)
                                plt.yticks(size = 5)
                                plt.show()
                                show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                fig.savefig(save_to_path+'/'+date1+date2+'summer.png')
                                
                                #Vols
                                vols = lidardem1 * pixelsize
                                print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
     
                            elif new.shape < old.shape:
                                  print('elif 1')
                                  ## Use the bounding box of the newer raster - making shapefile to clip by
                                  
                                  boundbox  = newer.bounds
                                  geom = box(*boundbox)
                                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                                 
                                  #   ###Shapefile
                                  df.to_file(path+'boundary.shp')
                                  with fiona.open(path+'boundary.shp','r') as shapefile:
                                        shapes = [feature['geometry'] for feature in shapefile]

                                    ###Clip older mask by newer shapefile
                                  out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True,  nodata = -9999.0)
                                  out_meta = newer.meta
                
                                  out_meta.update({'driver':'GTiff', 'count':1,'height':newer.shape[0],'width':newer.shape[1],'transform':out_transform})
                                  ###maybe change height according to new shape and old shape.
                                    
                                  with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                          dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                          dest.write(out_image)
                                  olderimage = rio.open(path+date1+date2+'bounding.tif')
                
                                  old = np.array(olderimage.read(1),dtype = rasterio.float32)
                                  

                                  imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                                  imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))

                               
                                  imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                                  imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
                
                                  
                                  mask1 = np.ma.getmask(imagenewmask)
                                  mask2 = np.ma.getmask(imageoldmask)
                            
                                  mask = np.logical_or(mask1,mask2)
                                  
                                  x = np.empty(newer.read(1).shape, dtype = rasterio.float32)
                
                                  x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                                  x = np.ma.array(x, mask = (mask))
                                  
                                  with rio.open(path+date1+date2+'summer.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1)
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                      
                                  lidardem = rio.open(path+date1+date2+'summer.tif')
                                  
                                  lidardem1 = np.array(lidardem.read(1))
                 
                                  lidardem1 = np.ma.array(lidardem1, mask=(mask))
                                  

                                  fig = matplotlib.pyplot.figure()
                                  ax = fig.add_subplot(1,1,1)
                                  
                                  norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
                                  show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,) 
                                  ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)    
                                  cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                  plt.xticks(size = 5)
                                  plt.yticks(size = 5)
                                  plt.tight_layout() 
                                  plt.show()
                                  show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                  fig.savefig(save_to_path+'/'+date1+date2+'summer.png')   
                                  
                                  #Vols
                                  vols = lidardem1 * pixelsize
                                  print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")

                            elif new.shape > old.shape:   
                                
                                  print('elif2')
                                    ##Older bounding box shape
                                  x = np.empty(older.read(1).shape, dtype = rasterio.float32)
                                  
                                  boundbox  = older.bounds
                                  geom = box(*boundbox)
                                  df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                                 
                                  df.to_file(path+'boundary.shp')
                                  with fiona.open(path+'boundary.shp','r') as shapefile:
                                      shapes = [feature['geometry'] for feature in shapefile]
                                      
                
                                  out_image, out_transform = rasterio.mask.mask(newer, shapes, crop=True, filled = True, nodata = -9999.0)
                                  
                                  out_meta = older.meta
                
                                  out_meta.update({'driver':'GTiff','count':1, 'height':older.shape[0],'width':older.shape[1],'transform':out_transform})
                               
                                  with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                          dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                          dest.write(out_image)
                                          
                                  newerimage = rio.open(path+date1+date2+'bounding.tif')
                                  
                                  new = np.array(newerimage.read(1),dtype = rasterio.float32)
                                  
                                  imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                                  imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))
                
                                  imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                                  imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
                
                                  mask1 = np.ma.getmask(imagenewmask)
                                  mask2 = np.ma.getmask(imageoldmask)
                            
                                  mask = np.logical_or(mask1,mask2)
                
                                  x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                
                                  x = np.ma.array(x, mask = (mask))
                
                                  with rio.open(path+date1+date2+'summer.tif','w',**out_meta) as dest:
                                      dest.write(x.filled(fill_value = -9999.0), 1) 
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                  
                                  lidardem = rio.open(path+date1+date2+'summer.tif')   
                                  lidardem1 = np.array(lidardem.read(1))
                                  lidardem1 = np.ma.array(lidardem1, mask=(mask))

                                  fig = matplotlib.pyplot.figure()
                                  ax = fig.add_subplot(1,1,1) 
                            
                                  norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
                                  show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform,)
                                  ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)     

                                  cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                                  cbar.set_label('Elevation Change (m)', rotation=270)
                                  plt.tight_layout()
                                  plt.xticks(size = 5)
                                  plt.yticks(size = 5)
                                  plt.show()
                                  show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                                  fig.savefig(save_to_path+'/'+date1+date2+'summer.png')
                                  
                                  #Volume
                                  vols = lidardem1 * pixelsize
                                  print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
                                  
                                  
                            summerdic[date1+'-'+date2] = {'Volumes': np.sum(vols), 'Date':['%s - %s' %(date1[4:7]+'/'+date1[0:4], date2[4:7]+'/'+date2[0:4])]} 
                        else:
                                break
                with open (save_to_path+'/summerdic.pkl', 'wb') as fb:
                                    pickle.dump(summerdic, fb, protocol = pickle.HIGHEST_PROTOCOL)
                DOD  = pd.DataFrame(summerdic)
                DOD = DOD.T
                return  DOD   
#%%
def autumnDOD(path, pixelsize, save_to_path, DODCRS):
            maskglobresults = [sorted(glob.glob(path+"*masked.tif"))]
            
            num = (len(sorted(glob.glob(path+"*masked.tif")))-1) 
            seasonfile = []
            for i in maskglobresults[0]:
                
                if re.search('[0-9][0-9][0-9][0-9][0-0][9-9]masked.tif',i):
                    seasonfile.append(i)
                elif re.search('[0-9][0-9][0-9][0-9][1-1][0-1]masked.tif',i):
                    seasonfile.append(i)                    
                else:
                    continue
            num = (len(seasonfile)-1)
            DODdic = {}
            for e, i in enumerate(seasonfile):
            ###use the counter to index the mask glob results list [0]
                    if e < num:
                        
                        older = rio.open(i)
                        newer = rio.open(seasonfile[seasonfile.index(i)- len(seasonfile)+1])
            
            
                        date1 = (i[-16:-10])
                        date2 = (seasonfile[seasonfile.index(i)- len(seasonfile)+1][-16:-10])
            
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
                              
                              x = np.ma.array(x, mask = (mask))
                            
                              out_meta = newer.meta
                              with rio.open(path+date1+date2+'autumn.tif','w',**out_meta) as dest:
                                    dest.write(x.filled(fill_value = -9999.0), 1)
                                    dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)

                            
                            ###PLOT FUNC
                             
                              lidardem = rio.open(path+date1+date2+'autumn.tif')
                              lidardem1 = np.array(lidardem.read(1))
                              lidardem1 = np.ma.array(lidardem1, mask=(mask))
                            

                              fig = matplotlib.pyplot.figure()
                              ax = fig.add_subplot(1,1,1)
                      
                              norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
                              show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm,transform = lidardem.transform,)

                              ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10)    
                              cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                              
                              plt.xticks(size = 5)
                              plt.yticks(size = 5)
                              plt.show()
                              show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                              fig.savefig(save_to_path+'/'+date1+date2+'autumn.png')
                              
                              vols = lidardem1 * pixelsize
                              print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n") 
                              DODdic[date1+'-'+date2] = {'Volumes': np.sum(vols), 'Date':['%s - %s' %(date1[4:7]+'/'+date1[0:4], date2[4:7]+'/'+date2[0:4])]} 

                        elif new.shape < old.shape:
                              print('elif 1')
                              ## Use the bounding box of the newer raster - making shapefile to clip by
                              
                              boundbox  = newer.bounds
                              geom = box(*boundbox)
                              df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                              df = df.set_crs(DODCRS)
                              #   ###Shapefile
                              df.to_file(path+'boundary.shp')
                              with fiona.open(path+'boundary.shp','r') as shapefile:
                                    shapes = [feature['geometry'] for feature in shapefile]
         
                                ###Clip older mask by newer shapefile
                              out_image, out_transform = rasterio.mask.mask(older, shapes, crop=True, filled = True,  nodata = -9999.0)
                              out_meta = newer.meta
            
                              out_meta.update({'driver':'GTiff',"count":1, 'height':newer.shape[0],'width':newer.shape[1],'transform':out_transform})
                              ###maybe change height according to new shape and old shape.
                                
                              with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                      dest.write(out_image)
                                      
                              olderimage = rio.open(path+date1+date2+'bounding.tif')
                              old = np.array(olderimage.read(1),dtype = rasterio.float32)
                                           
                              imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                              imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))
                           
                              imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                              imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
             
                              mask1 = np.ma.getmask(imagenewmask)
                              mask2 = np.ma.getmask(imageoldmask)
                        
                              mask = np.logical_or(mask1,mask2)
                              
                              x = np.empty(newer.read(1).shape, dtype = rasterio.float32)
            
                              x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
                              x = np.ma.array(x, mask = (mask))
                              with rio.open(path+date1+date2+'autumn.tif','w',**out_meta) as dest:
                                  dest.write(x.filled(fill_value = -9999.0), 1)
                                  
                              lidardem = rio.open(path+date1+date2+'autumn.tif')
                              
                              lidardem1 = np.array(lidardem.read(1))
             
                              lidardem1 = np.ma.array(lidardem1, mask=(mask))
                              fig, ax = plt.subplots(1, figsize=(5,5)) 
                              
                              
                              norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
                              show((lidardem1) , ax = ax, cmap='seismic_r', norm = norm, transform = lidardem.transform,)
                              ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10) 
                              cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                              plt.xticks(size = 5)
                              plt.yticks(size = 5)
                              plt.show()
                              show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                              fig.savefig(save_to_path+'/'+date1+date2+'autumn.png')
                              
                              vols = lidardem1 * pixelsize
                              print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
                              DODdic[date1+'-'+date2] = {'Volumes': np.sum(vols), 'Date':['%s - %s' %(date1[4:7]+'/'+date1[0:4], date2[4:7]+'/'+date2[0:4])]} 

                        elif new.shape > old.shape:   
                            
                              print('elif2')
                                ##Older bounding box shape
                              x = np.empty(older.read(1).shape, dtype = rasterio.float32)
                              
                              boundbox  = older.bounds
                              geom = box(*boundbox)
                              df = gpd.GeoDataFrame({'id':1,'geometry':[geom]})
                              df = df.set_crs(DODCRS)
                              df.to_file(path+'boundary.shp')
                              with fiona.open(path+'boundary.shp','r') as shapefile:
                                  shapes = [feature['geometry'] for feature in shapefile]
                                  
            
                              out_image, out_transform = rasterio.mask.mask(newer, shapes, crop=True, filled = True, nodata = -9999.0)
                              
                              out_meta = older.meta
            
                              out_meta.update({'driver':'GTiff','count':1, 'height':older.shape[0],'width':older.shape[1],'transform':out_transform})
                           
                              with rio.open(path+date1+date2+'bounding.tif','w', **out_meta) as dest:
                                      dest.crs = rasterio.crs.CRS.from_epsg(DODCRS)
                                      dest.write(out_image)
                                      
                              newerimage = rio.open(path+date1+date2+'bounding.tif')
                              
                              new = np.array(newerimage.read(1),dtype = rasterio.float32)
                              
                              imagenewmask = np.ma.array(new, mask = (new == -9999.0))
                              imagenewmask = np.ma.array(imagenewmask, mask = (imagenewmask == 0.0))
            
                              imageoldmask = np.ma.array(old, mask = (old == -9999.0))
                              imageoldmask = np.ma.array(imageoldmask, mask = (imageoldmask == 0.0))
            

                              mask1 = np.ma.getmask(imagenewmask)
                              mask2 = np.ma.getmask(imageoldmask)
                        
                              mask = np.logical_or(mask1,mask2)
            
                              x = np.where(((~imagenewmask.mask)&(~imageoldmask.mask)), imagenewmask - imageoldmask, x)
            
                              x = np.ma.array(x, mask = (mask))
            
                              with rio.open(path+date1+date2+'autumn.tif','w',**out_meta) as dest:
                                  dest.write(x.filled(fill_value = -9999.0), 1)    
                              
                              lidardem = rio.open(path+date1+date2+'autumn.tif')
                              
                              
                              lidardem1 = np.array(lidardem.read(1))
                              masky = lidardem.read_masks(1)
            
                              lidardem1 = np.ma.array(lidardem1, mask=(mask))
                              
                              fig, ax = plt.subplots(1, figsize=(5,5)) 
                        
                              norm = matplotlib.colors.TwoSlopeNorm(vmin = lidardem1.min(), vcenter = 0, vmax= lidardem1.max())
                              show((lidardem1) , ax = ax, cmap='seismic_r',norm = norm, transform = lidardem.transform)
                              ax.set_title('DOD %s - %s' %(date1[4:7]+"/"+date1[0:4], date2[4:7]+"/"+date2[0:4]),fontsize=10) 
                              cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap = 'seismic_r'), ax = ax)
                              plt.xticks(size = 5)
                              plt.yticks(size = 5)
                              plt.show()
                              show_hist(lidardem1, bins=10, histtype='stepfilled', lw=0.0, stacked=True, alpha=0.3)
                              fig.savefig(save_to_path+'/'+date1+date2+'autumn.png')
                              
                              vols = lidardem1 * pixelsize
                              print("\nThe total volume of change is \n", np.sum(vols), "\n(m3)\n")
                              DODdic[date1+'-'+date2] = {'Volumes': np.sum(vols), 'Date':['%s - %s' %(date1[4:7]+'/'+date1[0:4], date2[4:7]+'/'+date2[0:4])]} 

            DOD  = pd.DataFrame(DODdic)
            DOD = DOD.T
            return  DOD  