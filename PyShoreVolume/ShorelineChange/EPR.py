#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 18:32:19 2023

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


gpd.options.display_precision = 10

def EPR(intersectednew, CRS, save_to_path, ellipsoidal):
                    """
                    Measures the rates of accretion or erosion throughout time. 
                
                    Parameters
                    ----------
                    intersectednew : Pandas GeoDataFrame
                        Geodataframe containing 'TR_ID' field of transect numbers, 'Year' field 
                        with YYYYMM values, 'geometry_x' field of each  shorlein intersection.
                        point. 
                    CRS : Integer Variable
                        Coordinate reference system to be used. 
                    ellipsoidal : String Variable
                        Ellipsoid type to be used in distance measurements. 
                
                        
                    Returns
                    -------
                    eprdic: Dictionary
                        Dictionary of End Point Rate calculations with transect number as key
                        values, with associated coordinates of oldest and newest shore intersect.
                
                    """
                    val = min(intersectednew['TR_ID'])
                    eprdic = {}
                    uniquetrans = intersectednew.TR_ID.unique()


                    for e, ids in enumerate(uniquetrans):
                        # if e == val:      
                            # print(val, e, ids)

                            s = GeoDataFrame(intersectednew.loc[intersectednew['TR_ID'] == ids])
                            # print(s['layer'])
                            newestdate = max(s['layer'])
                            oldestdate = min(s['layer'])
                            
                            newestdatedate = datetime(year=int(newestdate[0:4]), month=int(newestdate[4:6]), day = int(newestdate[6:8]))
                            oldestdatedate = datetime(year=int(oldestdate[0:4]), month=int(oldestdate[4:6]), day = int(oldestdate[6:8]))
                            
                            transy = np.array(s['Y'])
                            transx = np.array(s['X'])
                            
                            
                                              
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
                                
                            transgeoms = np.vstack((transx, transy)).T
                            newdatedatageoms = np.vstack((newdategeomsx,newdategeomsy)).T
                            olddatedatageoms = np.vstack((olddategeomsx,olddategeomsy)).T

                            ###EPR Calculation of UTM coords to euclidean distance. 
                            distancesbetweendates = cdist(newdatedatageoms, olddatedatageoms, 'euclidean')

                            
                            ####this section is to allow the chosen CRS nad ellipsoid to be defined when measuring actual distance. 
                            gpdfirst, gpdsecond = pd.DataFrame({'x':[newdatedatageoms[0,0]],'y':[newdatedatageoms[0,1]]}, columns = ['x','y']), pd.DataFrame({'x':[olddatedatageoms[0,0]],'y':[olddatedatageoms[0,1]]}, columns = ['x','y'])
                            firstdata = GeoDataFrame(gpdfirst, geometry = gpd.points_from_xy(gpdfirst['x'],gpdfirst['y']), crs = CRS)
                            seconddata = GeoDataFrame(gpdsecond, geometry = gpd.points_from_xy(gpdsecond['x'],gpdsecond['y']), crs = CRS) 
                            
         
                            coordinate1 = (np.array(firstdata['geometry'].y), np.array(firstdata['geometry'].x))
                            coordinate2 = (np.array(seconddata['geometry'].y), np.array(seconddata['geometry'].x))
                            distances = geopy.distance.geodesic(coordinate1,coordinate2, ellipsoid = ellipsoidal).m                           
                            
                            timediff = pd.Series(newestdatedate - oldestdatedate)/pd.to_timedelta(1, unit='D')
                            # print(timediff)
                            timelength = timediff[0]/365.2425
      
                            #####JJUST FOR CORR AGAINST AMBUR!!!######
                            euceprresult = distancesbetweendates/timelength
                            
                            #ERROR
                            georeferencingerrornew = s['Georef Err'].loc[s['layer'] == newestdate]
                            measurementerrornew = s['Measurement Err'].loc[s['layer'] == newestdate]
                            newerr = float(georeferencingerrornew + measurementerrornew)
                            
                            
                            georeferencingerrorold = s['Georef Err'].loc[s['layer'] == oldestdate]
                            measurementerrorold = s['Measurement Err'].loc[s['layer'] == oldestdate]
                            olderr = float(georeferencingerrorold + measurementerrorold)
                            
                            ##Actual distance. 
                            eprresult = distances/timelength
                            
                            eprerror = (math.sqrt((newerr ** 2)+(olderr ** 2)))/timelength
                            ##distance to transects (allows a +/- to be given to EPR Calculation)
                            distanceold = cdist(olddatedatageoms, transgeoms, 'euclidean')
                            distancenew = cdist(newdatedatageoms, transgeoms, 'euclidean')
                            
                            #Finding coords of max distcances
                            maxs = np.max(distancesbetweendates)
                            location = np.where(distancesbetweendates == maxs)  

                            
                            if distanceold[0][0] < distancenew[0][0]:
                                eprresult = -abs(eprresult)
                                euceprresult = -abs(euceprresult[0][0])                               
                                distancesbetweendates = -abs(distancesbetweendates[0][0])                             
                                distances = -abs(distances)
                               
  
                                
                            else:
                                eprresult = eprresult
                                distancesbetweendates = distancesbetweendates[0][0]
                                euceprresult = euceprresult[0][0]
    
                            # eprerrorpos = eprresult + eprerror
                            # eprerrorneg = eprresult - eprerror    
                            
                            # print(olddatedatageoms[location[1][0]])
                            eprdic[ids]= { 'Oldest date coords': coordinate1,'Oldest date':oldestdatedate,
                                          'Newest date coords':coordinate2, 'Newest date': newestdatedate, 
                                          'EPR':eprresult, 'Euclidean EPR':euceprresult, 'Transect':ids,'Total distance':distances,
                                           'EPRerr':eprerror, 'Euclidean distance': distancesbetweendates, 
                                           }    
                            val = val + 1

                            
                    eprvals= []
                    eprerr = []
                    
                    transects = []
                    for e, i in eprdic.items():
                        transects.append(e)
                        # print(e)
                        eprvals.append(i['EPR'])
                        eprerr.append(i['EPRerr'])
                        # eprerrneg.append(i['EPRerrneg'])
                        # print(eprerrneg,eprerrpos)
                    
                    # transects.reverse() ###To get transects going from south to north!
                    
                    fig = plt.figure(figsize=(5,15))
                    ax = fig.add_subplot(111)
                    
                    ax.scatter(eprvals,transects, s=2, marker = 'o')
                    ax.errorbar(eprvals,transects, xerr = eprerr)
                    # ax.plot(eprerrpos, transects)
                    # ax.plot(eprerrneg, transects)
                    ax.grid()
                    ax.set_ylabel('Transect Number', fontsize = 12)
                    ax.set_xlabel('EPR Rate (m/yr)', fontsize = 12)
                    
                    plt.show()
                    fig.savefig(save_to_path+'End Point Rate.png', bbox_inches='tight')

                    print("\nMaximum End Point Rate (Accretion): \n", max(eprvals))
                    print("\nMinimum End Point Rate (Erosion) : \n", min(eprvals))
                    with open (save_to_path+'/eprresults.pkl', 'wb') as fb:
                        pickle.dump(eprdic, fb, protocol = pickle.HIGHEST_PROTOCOL)
                    
                    
                    eprdic = pd.DataFrame(eprdic)
                    eprdic = eprdic.T
                    
                    return eprdic
                        
                                                