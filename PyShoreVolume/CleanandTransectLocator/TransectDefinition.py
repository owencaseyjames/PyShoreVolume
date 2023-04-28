#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 13:16:41 2022

@author: owenjames
"""

#TransectDefinition.py


#imports geoplot as gplt
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


##Number 1
###Add transect points to geodataframe (X AND Y are transect root coord from the linestring) Number 1
###If wrong way around the erosion and accretion values  will be the wrong way around. Baseline m
def transectstartlocator1(baseline, intersectednew):
        """
        Locates the starting coordinates of each transect and merges them into the 
        into the intersection data frame.
    
        Parameters
        ----------
        baseline : Pandas GeoDataframe 
            GeoDataframe of cross transects shapefile
        intersectednew : Pandas GeoDataframe
            Geodataframe containing 'TR_ID' field of transect numbers, 'layer' field 
            with YYYYMM integer values, 'geometry_x' field of each shoreline intersection,
    
        Returns
        -------
        intersected: Pandas GeoDatafame
             Geodataframe of the intersect file with the correspondng coordinates of
             the transect starting point on the seaward side in the fields 'X' and 'Y'.
             Allows Erosion/Accretion rates to be measured in other functions.
    
        """
        x = []
        y = []
        trid = []
        val = 0
        for i in baseline['geometry']:
            # print(baseline['geometry'][val].coords[1])
            x.append(baseline['geometry'][val].coords[1][0])
            y.append(baseline['geometry'][val].coords[1][1])
            trid.append(baseline['TR_ID'][val])
            val = val + 1
        transectgeoms = GeoDataFrame({'X':x,'Y':y,'TR_ID':trid})
        transectgeoms = GeoDataFrame(transectgeoms, geometry=gpd.points_from_xy(transectgeoms.X,transectgeoms.Y))
        transectgeoms.plot()
        
        if 'X' in intersectednew.columns: 
            transectgeoms.set_index('TR_ID').combine_first(intersectednew.set_index('TR_ID'))            
        else:    
            intersectednew = intersectednew.merge(transectgeoms, on='TR_ID', how= 'left')      
        intersected = intersectednew.set_geometry('geometry_x')
        
        return intersected

### Number 2
##If transect and thus baseline start locations are on the other sifde of the transect 
def transectstartlocator2(baseline, intersectednew):
        """
        ocates the starting coordinates of each transect and merges them into the 
        into the intersection data frame.
        
        Parameters
        ----------
        baseline : Pandas GeoDataframe 
            GeoDataframe of cross transects shapefile
        intersectednew : Pandas GeoDataframe
            Geodataframe containing 'TR_ID' field of transect numbers, 'layer' field 
            with YYYYMM integer values, 'geometry_x' field of each shoreline intersection,
    
        Returns
        -------
        intersected: Pandas GeoDatafame
             Geodataframe of the intersect file with the correspondng coordinates of
             the transect starting point on the seaward side in the fields 'X' and 'Y'.
             Allows Erosion/Accretion rates to be measured in other functions.
        """
        x = []
        y = []
        trid = []
        val = 0
        for i in baseline['geometry']:
            # print(baseline['geometry'][val].coords[0])
            x.append(baseline['geometry'][val].coords[0][0])
            y.append(baseline['geometry'][val].coords[0][1])
            trid.append(baseline['TR_ID'][val])
            val = val + 1
        transectgeoms = GeoDataFrame({'X':x,'Y':y,'TR_ID':trid})
        transectgeoms = GeoDataFrame(transectgeoms, geometry=gpd.points_from_xy(transectgeoms.X,transectgeoms.Y))
        transectgeoms.plot()
        
        if 'X' in intersectednew.columns: 
            transectgeoms.set_index('TR_ID').combine_first(intersectednew.set_index('TR_ID'))
        else:    
            intersectednew = intersectednew.merge(transectgeoms, on='TR_ID', how= 'left')
            
        intersected = intersectednew.set_geometry('geometry_x')
        
        return intersected
    
        

# if __name__ =='__main__':
#     sys.exit()
    
####DECIDE IF WE WILL GO AHEAD WITH THIS (MULTIPLE CONTOUR VALUES)
###Set geometry column now that Geometry x is the coords of the intersected point
# intersected = intersected.set_geometry('geometry_x')

# ###Extract the intersections of contours produced from errors
# lowerranges = GeoDataFrame(intersected.loc[intersected['Z']== intersected['Z'].min()])
# lowerranges = lowerranges.set_geometry('geometry_x')


# higherranges = intersected.loc[intersected['Z']== intersected['Z'].max()]
# # higherranges['TR_ID'] = higherranges['TR_ID'].astype(int)
# # higher = GeoDataFrame(intersectednew.loc[intersectednew['Z']== intersectednew['Z'].max()])
# higherranges= higherranges.set_geometry('geometry_x')
# print(max(higherranges['TR_ID']))
# print(max(lowerranges['TR_ID']))
# highers.TR_ID.dtype

