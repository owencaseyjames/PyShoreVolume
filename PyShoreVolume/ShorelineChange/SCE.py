#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 17:35:27 2023

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

import math

def SCE(intersectednew, transectplot, CRS, ellipsoidal,save_to_path):
                                scedic = {}
                                val = min(intersectednew['TR_ID'])
                                data = []
                                distances=[]
                                coordx = []
                                coordy = []
                                trid = []
                                distances1 = []
                                trloc = math.ceil((max(intersectednew['TR_ID'])/transectplot)/2)*2
                        
                                uniquetrans = intersectednew.TR_ID.unique()
                                for e, ids in enumerate(uniquetrans):
                                    # if ids == val:            
                                        s = intersectednew.loc[intersectednew['TR_ID'] == ids]
                                        s = s.sort_values('layer')
                                        transectsvalx = np.array(s['geometry_x'].x)
                                        transectsvaly = np.array(s['geometry_x'].y)
                                        transectsval = np.vstack((transectsvalx, transectsvaly)).T
                                        distancescdist = cdist(transectsval, transectsval,'euclidean') ##Identifies distances between points
                                        maxds = np.max(distancescdist) ##Identifies max distances  
                                        
                                        ##Location of max distances (to be used as index for coords and dates)
                                        location = np.where(distancescdist == maxds)
                                        
                                        #Find dates of max range 
                                        firstyear = s['layer'].iloc[location[0][0]]
                                        secondyear = s['layer'].iloc[location[0][1]]
                                        
                                        
                                        newdatedatadf= pd.DataFrame({'x':[transectsval[location[0][0]][0]],'y':[transectsval[location[0][0]][1]], 'x1':[transectsval[location[1][0]][0]],\
                                                                     'y1':[transectsval[location[1][0]][1]]}, columns=['x','y','x1','y1'])
                                        firstdata = GeoDataFrame(geometry = gpd.points_from_xy(newdatedatadf['x'],newdatedatadf['y']), crs = CRS)
                                        seconddata = GeoDataFrame(geometry = gpd.points_from_xy(newdatedatadf['x1'],newdatedatadf['y1']), crs = CRS)          
                                        

                                        firstdata = firstdata.to_crs(CRS)
                                        seconddata = seconddata.to_crs(CRS)
                                        coordinate1 = (np.array(firstdata['geometry'].y), np.array(firstdata['geometry'].x))
                                        coordinate2 = (np.array(seconddata['geometry'].y), np.array(seconddata['geometry'].x))
                                        distances = geopy.distance.distance(coordinate1,coordinate2, ellipsoid = ellipsoidal).m
                                                                      
                                        #Transform for mapping
                                        firstdata = firstdata.to_crs(3857)
                                        seconddata = seconddata.to_crs(3857)
####This dictionary isnt needed >
                                        scedic[ids] = {'First coordinate':coordinate1,'Second coordinate':coordinate2, 
                                                       'Transect':ids,'Distances': distances, 'Newest date': firstyear, 
                                                       'Oldest date':secondyear} 
                                        ##Saves coords and distances in dictionary
                                    
                                        coordx.append(firstdata['geometry'].x)
                                        coordy.append(firstdata['geometry'].y)
                                        coordx.append(seconddata['geometry'].x)
                                        coordy.append(seconddata['geometry'].y)
                                        distances1.append(distances)
                                        distances1.append(distances)
                                        trid.append(ids)
                                        trid.append(ids)
                                            

                                
                                norm = matplotlib.colors.Normalize(vmin = min(distances1), vmax= max(distances1), clip = True)
                                cmaps= plt.get_cmap('viridis')
                                c = cmaps(norm(distances1))
                                fig = plt.figure(figsize=(10,20))
                                ax = fig.add_subplot(111)
                                
                                for i in range(0,len(coordx),2):
                                    ax.plot(coordx[i:i+2],coordy[i:i+2],marker = None, c=c[i])
                                for ins in range(0,len(trid),trloc):                    
                                    ax.annotate(trid[ins], (coordx[ins], coordy[ins]))                              
                                
                                
                                divider = make_axes_locatable(ax)
                                cax = divider.append_axes("right", size="5%", pad=0.05)    
                                cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap = cmaps), ax = ax, cax = cax)
                                cbar.set_label('Change in Meters', rotation=270, fontsize = 13, labelpad = 12)
                                ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=15)
                                ax.set_title('Shoreline Change Envelope', fontsize=15)
                                ax.set_ylabel('Latitude', fontsize = 12)
                                ax.set_xlabel('Longitude', fontsize=12)
                                plt.show()
                                fig.savefig(save_to_path+'shorleinechangeenvelope.png',bbox_inches='tight')
                                
                                with open (save_to_path+'/scedic.pkl', 'wb') as fb:
                                    pickle.dump(scedic, fb, protocol = pickle.HIGHEST_PROTOCOL)   
                                
                                scedic = pd.DataFrame(scedic)
                                scedic = scedic.T
                                return scedic
                                
                            