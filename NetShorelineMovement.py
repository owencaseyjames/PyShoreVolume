#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 18:17:20 2023

@author: owenjames
"""


import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
import pandas as pd

import os 

import scipy
from scipy.spatial import ConvexHull, convex_hull_plot_2d
from scipy.spatial.distance import cdist, pdist

import statsmodels.api as sm

import numpy as np

import shapely
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points

import sklearn
from sklearn import preprocessing
from sklearn import linear_model
from sklearn.linear_model import LinearRegression 
from sklearn.metrics import r2_score, mean_squared_error

import seaborn as sns

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.lines import Line2D

import contextily as ctx

import pyproj

import time

import datetime
from datetime import datetime, timezone

import geopy.distance
 
import pickle

import sys

import Config 


def netshorelinemovement(intersectednew, CRS, ellipsoidal):
               coordx = []
               coordy = []
               transects = []
               transects2 = []
               distances1 = []
               trid=[]
               val = min(intersectednew['TR_ID'])
               nsmdic = {}
               uniquetrans = intersectednew.TR_ID.unique()

               for e, ids in enumerate(uniquetrans):
                        # print(ids)
                       if val == e:             
                          s = GeoDataFrame(intersectednew.loc[intersectednew['TR_ID'] == ids])
                          # print(s.columns)ko
                          newestdate = max(s['layer'])
                          oldestdate = min(s['layer'])
                          print(newestdate, oldestdate)
                          for i in s['layer']:
                                 if i == oldestdate:
                                        oldgeoms = s.loc[s['layer']==i]
                                        print(oldgeoms['ID'])
                                        olddategeomsx = np.array(oldgeoms['geometry_x'].x)
                                        olddategeomsy = np.array(oldgeoms['geometry_x'].y)                                       
                                        continue
                      
                          for i in s['layer']:
                                 if i == newestdate:
                                        newgeoms = s.loc[s['layer']==i]
                                        print(newgeoms['ID'])
                                        newdategeomsx = np.array(newgeoms['geometry_x'].x)
                                        newdategeomsy = np.array(newgeoms['geometry_x'].y)
                                        continue
                          newdatedatageoms = np.vstack((newdategeomsx,newdategeomsy)).T
                          olddatedatageoms = np.vstack((olddategeomsx,olddategeomsy)).T

                                                                 
                          gpdfirst, gpdsecond = pd.DataFrame({'x':[newdatedatageoms[0,0]],'y':[newdatedatageoms[0,1]]}, columns = ['x','y']), pd.DataFrame({'x':[olddatedatageoms[0,0]],'y':[olddatedatageoms[0,1]]}, columns = ['x','y'])
                          firstdata = GeoDataFrame(gpdfirst, geometry = gpd.points_from_xy(gpdfirst['x'],gpdfirst['y']), crs = 4326)
                          seconddata = GeoDataFrame(gpdsecond, geometry = gpd.points_from_xy(gpdsecond['x'],gpdsecond['y']), crs = 4326) 
                          print(firstdata['geometry'], seconddata['geometry'])
                          firstdata = firstdata.to_crs(CRS)
                          seconddata = seconddata.to_crs(CRS)
                
                          coordinate1 = (np.array(firstdata['geometry'].x), np.array(firstdata['geometry'].y))
                          coordinate2 = (np.array(seconddata['geometry'].x), np.array(seconddata['geometry'].y))
                          distances = geopy.distance.distance(coordinate1,coordinate2, ellipsoid = ellipsoidal).m
                           
                          
                            
                          nsmdic[ids] = {'Newestdatecoords':coordinate1,'Newestdate':newestdate, 'Oldestdate':oldestdate, \
                                        'Oldestdatecoords':coordinate2, 'Distance':distances}
                          firstdata = firstdata.to_crs(3857)
                          seconddata = seconddata.to_crs(3857)

                          coordx.append(firstdata['geometry'].x)
                          coordy.append(firstdata['geometry'].y)
                          coordx.append(seconddata['geometry'].x)
                          coordy.append(seconddata['geometry'].y)
                          distances1.append(distances)
                          distances1.append(distances)
                          trid.append(ids)
                          trid.append(ids)
                          val = val+1
                          
               norm = matplotlib.colors.Normalize(vmin = min(distances1), vmax= max(distances1), clip = True)
               cmaps= plt.get_cmap('viridis')
               c = cmaps(norm(distances1))
               fig = plt.figure(figsize=(10,20))
               ax = fig.add_subplot(111)
                            
               for i in range(0,len(coordx),2):
                    ax.plot(coordx[i:i+2],coordy[i:i+2],'ro-',marker = None, c=c[i]) 
               for ins in range(0,len(trid),100):                    
                    ax.annotate(trid[ins], (coordx[ins], coordy[ins]))  
                    
               divider = make_axes_locatable(ax)
               cax = divider.append_axes("right", size="5%", pad=0.05)           
               cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap = cmaps), ax = ax, cax = cax)
               cbar.set_label('Change in Meters', rotation=270,fontsize = 13, labelpad = 12)
               ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=15)
               ax.set_title('Net Shoreline Change', fontsize=15)
               ax.set_ylabel('Latitude', fontsize = 12)
               ax.set_xlabel('Longitude', fontsize=12)
               plt.show()         
               fig.savefig(Config.save_to_path+'/netshorelinemovement.png')


               with open (Config.save_to_path+'/nsm.pkl', 'wb') as fb:
                   pickle.dump(nsmdic, fb, protocol = pickle.HIGHEST_PROTOCOL)