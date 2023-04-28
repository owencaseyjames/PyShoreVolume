#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 15:09:47 2023

@author: owenjames
"""
#DataCleaning.py


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

import datetime
from datetime import datetime

import pickle


def cleaning(intersected):
        """
        Data cleaning protocol to remove duplicate intersections of the same year
        along the same transect only keeping one that is closest to the seaward 
        side from the intersections with no 'layer' value. 
    
        Parameters
        ----------
        intersected : Pandas GeoDataframe
            Geodataframe containing 'TR_ID' field of transect numbers, 'layer' field 
            with YYYYMM integer values, 'geometry_x' field of each shoreline intersection,
            and 'geometry_y' of each transect starting location. 
            
    
        Returns
        -------
        intersectednew : Pandas GeoDataFrame
            Geodataframe that only contains the closet intersect to the shoreline from 
            that date, with all other intesects removed. Also removes any intersection
            point that do not have a value in the 'layer' column to identify their date.
        """
    
        intersected = intersected.sort_values(by=['TR_ID'])
        uniquetrans = intersected.TR_ID.unique()
        val = int(min(intersected['TR_ID']))
        listy = []

        dicty = {}
        for e, ids in enumerate(uniquetrans):
                # if val == ids: 
                # print(ids, e)
                s = GeoDataFrame(intersected.loc[intersected['TR_ID'] == ids])
                # print(s)
                # s = s.loc[s['Z']== median]
                s = s.set_geometry('geometry_x').to_crs(epsg=3857)
                ##tr - transect geometry point
                tr = s
                tr = tr.set_geometry('geometry_y').to_crs(epsg=3857)
                uniquelayer = s['layer'].drop_duplicates()
                #print(tr, uniquelayer)      
        
         ####Iterate through the available years taking the intersect closest to baseline first
        
                for i in uniquelayer:
                    yeardrop = s.loc[s['layer']==i]
                    trs = tr.iloc[0]
                    # print(trs)
                    dists = yeardrop['geometry_x'].distance(trs['geometry_y'])
                    # print(dists)
                    gdf1 = intersected.loc[dists.idxmin()]
                    gdf1 = gdf1.T
                    dicty = {}
                    dicty.update(gdf1)
                    listy.append(dicty)     
                
        
        intersectednew = GeoDataFrame(listy)
        intersectednew = intersectednew.set_geometry('geometry_x') 
        intersectednew = GeoDataFrame(intersectednew[~intersectednew['layer'].isnull()])
        return intersectednew
        #print(len(intersectednew))



###lower level
# vals = int(min(lowerranges['TR_ID']))
# listlower = []
# for ids in lowerranges['TR_ID']:
#     if vals == ids: 
#         # print(ids)
#         s = GeoDataFrame(lowerranges.loc[lowerranges['TR_ID'] == ids])
                        
#         #### find individual dates to use as the index
#         uniquelayer = s['layer'].drop_duplicates()
                
#         #####iterate through the available years taking the closest to baseline first
#         for i in uniquelayer:
#                 #             ###find the index of the first year in this transect
#                 indexes = s.loc[s['layer']==i].index[0]
#                 # print(indexes['ID'])
#                               ###Same for the upper and lower ranges
#                 indexlow = lowerranges[lowerranges['layer']==i].index[0]    
#                               # print(intersectednew.loc[indexes])
#                 gdf1 = lowerranges.loc[indexes]
#                 gdf1 = gdf1.T
#                 dicty = {}
#                 dicty.update(gdf1)
#                 listlower.append(dicty)
#         vals = vals + 1
# intersectedlower = GeoDataFrame(listlower)
# intersectedlower.rename(columns={'geometry_x':'geometry_lower','Z':'Z_lower'}, inplace=True)
# intersectedlower = intersectedlower.set_geometry('geometry_lower')


# # ####Higherlevel
# val = int(min(intersected['TR_ID']))
# listy = []
# maxi = max(intersected['Z'])
# # print(median)
# for ids in intersected['TR_ID']:
#     if val == ids: 
#         # print(ids)
#         s = GeoDataFrame(intersected.loc[intersected['TR_ID'] == ids])
#         s = s.loc[s['Z']== maxi]
        
# #       ### find individual dates to use as the index
#         uniquelayer = s['layer'].drop_duplicates()
        

# # #       ####iterate through the available years taking the closest to baseline first
#         for i in uniquelayer:
# #             ###find the index of the first year in this transect
#               indexes = s.loc[s['layer']==i].index[0]
#               ###Same for the upper and lower ranges
#               indexlow = lowerranges[lowerranges['layer']==i].index[0]
#               # print(intersectednew.loc[indexes])
#               gdf1 = intersected.loc[indexes]
#               gdf1 = gdf1.T
#               dicty = {}
#               dicty.update(gdf1)
#               listy.append(dicty)
#         val = val + 1
# intersectedhigher = GeoDataFrame(listy)
# intersectedhigher.rename(columns={'geometry_x':'geometry_higher','Z':'Z_higher'}, inplace=True)
# intersectedhigher = intersectedhigher.set_geometry('geometry_higher') 
# # print(intersectedhigher['Z'].max())
# # print(intersectedhigher)

# intersectednew = pd.merge(intersectednew,intersectedhigher[['TR_ID','layer','geometry_higher','Z_higher']], on = ['TR_ID','layer'])
# intersectednew = pd.merge(intersectednew,intersectedlower[['TR_ID','layer','geometry_lower','Z_lower']], on = ['TR_ID','layer'])
