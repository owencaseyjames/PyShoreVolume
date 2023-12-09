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


def cleaning(intersected, CRS):
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
                # if e > 277: 
                # print(ids, e)
                s = GeoDataFrame(intersected.loc[intersected['TR_ID'] == ids])
                # print(s)
                # s = s.loc[s['Z']== median]
                s = s.set_geometry('geometry_x')
                
                s = s.to_crs(epsg=3857)
                ##tr - transect geometry point
                tr = s
                tr = tr.set_geometry('geometry_y')
                tr = tr.set_crs(epsg= CRS, allow_override=True)
                tr = tr.to_crs(epsg=3857)
                print(tr['geometry_y'], s['geometry_x'])
                
                uniquelayer = s['layer'].drop_duplicates()
                #print(tr, uniquelayer)      
        
         ####Iterate through the available years taking the intersect closest to baseline first
        
                for i in uniquelayer:
                    yeardrop = s.loc[s['layer']==i]
                    trs = tr.iloc[0]
                    
                    dists = yeardrop['geometry_x'].distance(trs['geometry_y'])
                    
                    gdf1 = intersected.loc[dists.idxmin()]
                    gdf1 = gdf1.T
                    dicty = {}
                    dicty.update(gdf1)
                    listy.append(dicty)     
                
        
        intersectednew = GeoDataFrame(listy)
        intersectednew = intersectednew.set_geometry('geometry_x') 
        intersectednew = GeoDataFrame(intersectednew[~intersectednew['layer'].isnull()])
        return intersectednew



