#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 17:22:17 2023

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

from statistics import mean

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

import datetime
from datetime import datetime

import pickle

import math

def NSMEandA(intersectednew, transectplot, CRS, ellipsoidal, save_to_path):
               """
               Produces graphical output of Erosion and Accretion distances. 
                
               Parameters
               ----------
               intersectednew : Pandas GeoDataFrame
                    Geodataframe containing 'TR_ID' field of transect numbers, 'layer' field 
                    with YYYYMM integer values, 'geometry_x' field of each shoreline intersection,
                    and 'geometry_y' of each transect starting location. 
               CRS : Integer Variable
                    Coordinate reference system to be used. 
               ellipsoidal : String Variable
                    Ellipsoid type to be used in geo-distance measurements. 
            
               Returns
               -------
               nsmerrandacc : Dictionary
                    Dictionary of Net Shoreline Erosion/Accretion distances with transect 
                    ID number as key value, Newset and Oldest shoreline dates, coordinates 
                    of each date.
            
               """
               val = min(intersectednew['TR_ID'])
               nsmdic = {}
               coordx=[]
               coordy = []
               transects = []
               transects2 = []
               distances1 = []
               cols = []
               trid = []
               nsmerrandacc = {}
               uniquetrans = intersectednew.TR_ID.unique()
               trloc = math.ceil((max(intersectednew['TR_ID'])/transectplot)/2)*2
               
               for e, ids in enumerate(uniquetrans):
                      # if val == e:            
                          s = GeoDataFrame(intersectednew.loc[intersectednew['TR_ID'] == ids])
                          # print(s.columns)ko
                          newestdate = max(s['layer'])
                          oldestdate = min(s['layer'])
                          
                          #Got the transect point geom
                          transgeometryx = np.array(s['X'])
                          transgeometryy = np.array(s['Y'])
                          
                          for i in s['layer']:
                                 if i == oldestdate:
                                        oldgeoms = s.loc[s['layer']==i]
                                        olddategeomsx = np.array(oldgeoms['geometry_x'].x)
                                        olddategeomsy = np.array(oldgeoms['geometry_x'].y)                               
                                        continue
                      
                          for i in s['layer']:
                                 if i == newestdate:
                                        newgeoms = s.loc[s['layer']==i]
                                        newdategeomsx = np.array(newgeoms['geometry_x'].x)
                                        newdategeomsy = np.array(newgeoms['geometry_x'].y)
                                        continue
                                    
                          newdatedatageoms = np.vstack((newdategeomsx,newdategeomsy)).T
                          olddatedatageoms = np.vstack((olddategeomsx,olddategeomsy)).T
                          transgeoms = np.vstack((transgeometryx, transgeometryy)).T
                          #####Issue with newdate geoms - should remove duplicate date coords on one trans 
                          
                          distancesbetweenyears = cdist(newdatedatageoms,olddatedatageoms,'euclidean')
                          maxs = np.max(distancesbetweenyears)
                          location = np.where(distancesbetweenyears == maxs)
                          # geopy.distance.geodesic((transectsvalx,transectsvaly)).m
                          # print(location)
                          distanceold = cdist(olddatedatageoms, transgeoms, 'euclidean')
                          distancenew = cdist(newdatedatageoms, transgeoms, 'euclidean')
                                                   
                          # print(newdatedatageoms[location[0]][0][0])
                          newdatedatadf = pd.DataFrame(newdatedatageoms)
                          trannew = GeoDataFrame(newdatedatadf, geometry = gpd.points_from_xy(newdatedatadf[0],newdatedatadf[1]), crs = CRS)
                        
                          
                          olddatedatadf = pd.DataFrame(olddatedatageoms)
                          tranold = GeoDataFrame(olddatedatadf, geometry = gpd.points_from_xy(olddatedatadf[0],olddatedatadf[1]), crs = CRS)


                          firstdata = trannew.to_crs(CRS)
                          seconddata = tranold.to_crs(CRS)
                          coordinate1 = (np.array(firstdata['geometry'].y), np.array(firstdata['geometry'].x))
                          coordinate2 = (np.array(seconddata['geometry'].y), np.array(seconddata['geometry'].x))
                          distances = geopy.distance.distance(coordinate1,coordinate2, ellipsoid = ellipsoidal).m

                          tranold = tranold.to_crs(3857)
                          trannew = trannew.to_crs(3857)
                          

                          
                          if distanceold[0][0] < distancenew[0][0]:
                                 col = 'r'
                                 distances = -abs(distances)
                                 
                          elif distanceold[0][0] == distancenew[0][0]:
                                 col = 'y'
                          else:
                                 col = 'b'
                                 
                          nsmerrandacc[ids] = {'Distances':distances, 'Newest date coords': coordinate1,'Newest date':newestdate, \
                                               'Oldest date coords': coordinate2, 'Oldest date': oldestdate, ' Transect':ids}
                          val = val+1    
                                                
                          coordx.append(tranold['geometry'].x)
                          coordy.append(tranold['geometry'].y)
                          coordx.append(trannew['geometry'].x)
                          coordy.append(trannew['geometry'].y)
                          distances1.append(distances)
                          distances1.append(distances)
                          cols.append(col)
                          cols.append(col)
                          trid.append(ids)
                          trid.append(ids)
                          

               norm = matplotlib.colors.Normalize(vmin = min(distances1), vmax= max(distances1), clip = True)
               cmaps= plt.get_cmap('viridis')

               fig = plt.figure(figsize=(20,20))
               ax = fig.add_subplot(111)
                             
               for i in range(0,len(coordx),2):
                        ax.plot(coordx[i:i+2],coordy[i:i+2],marker = None, c=cols[i])    
               for ins in range(0,len(trid),trloc):                    
                         ax.annotate(trid[ins], (coordx[ins], coordy[ins]))  
                  # fig.colorbar(cm.ScalarMappable(norm=norm, cmap = cmaps), ax = ax)
               ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=15)
               
               plt.title('Net Shoreline Movement - Erosion and Accretion',fontsize=15 )
               erosiony = [Line2D([0],[0],color = 'r', lw = 4, label = 'Erosion'),
                           Line2D([0],[0],color = 'b', lw = 4, label = 'Accretion')]
               ax.legend(handles = erosiony)
               ax.set_ylabel('Latitude', fontsize = 12)
               ax.set_xlabel('Longitude', fontsize=12)
               plt.show()  
               fig.savefig(save_to_path+'/NetShorelineMovementErosionandAccretion.png',bbox_inches='tight')
               
               
               
               with open (save_to_path+'/nsmerrandaccdic.pkl', 'wb') as fb:
                   pickle.dump(nsmerrandacc, fb, protocol = pickle.HIGHEST_PROTOCOL)       
                   
               print("Maximum Erosion: {}".format(min(distances1)))
               print("Maximum Accretion: {}".format(max(distances1)))
               
               nsmerrandacc = pd.DataFrame(nsmerrandacc)
               nsmerrandacc = nsmerrandacc.T
               
               return nsmerrandacc
               
               
               