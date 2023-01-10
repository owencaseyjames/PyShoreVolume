#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 13:57:40 2023

@author: owenjames
"""
import sys 
import os

os.chdir('/Users/owenjames/Dropbox/PhD/Shoreline_Data/cco_data-20220625114304 Woola/data/lidar/')
path = '/Users/owenjames/Dropbox/PhD/Shoreline_Data/cco_data-20220625114304 Woola/data/lidar/'

sys.path.append(r'/Users/owenjames/Dropbox/PhD/Python_Scripts/ShorelineChangeAnalysisTool/')


import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
import pandas as pd


import TransectDefinition
from TransectDefinition import transectstartlocator

import DataCleaning
from DataCleaning import cleaning

import NetShorelineMovementErosionandAccretion
from NetShorelineMovementErosionandAccretion import netshorelinemovementerosionoracccretion

import NetShorelineMovement 
from NetShorelineMovement import netshorelinemovement

import EndPointRate
from EndPointRate import endpointrate

import LinearRegressionRate
from LinearRegressionRate import linearregressionrate

import MaskingDEM
from MaskingDEM import masking

import DEMofDifference 
from DEMofDifference import DEMofDifference

import DODSubPlot
from DODSubPlot import DODSubPlot

import OldesttoNewest
from OldesttoNewest import OldesttoNewestDOD

import LimitofDetection
from LimitofDetection import LimitofDetection 

import NetVolumeChange
from NetVolumeChange import NetVolumeChange

print('file two name is set to:{}'.format(__name__))

print(sys.path)
###Save to path 
directory = 'results/'
save_to_path = os.path.join(path, directory)
os.makedirs(save_to_path, exist_ok = True)
print(save_to_path)
#Extending amount of coordinates 
gpd.options.display_precision = 10

print(sys.path)


##May just have put all these in the config file. 
###ADD CRS VARIABLE TO THE DEM functions. 


##Desired CRS (Used in geopy measurements - go to site to find most suitable (27700 not available for SCA)
CRS = 4277

##Specify the crs ellipsoid (Used in geopy distance measurements - go to site to find mathing ellipsoid for crs)
ellipsoidal = 'Airy (1830)'


##Read in intersects shapefile 
intersectdata = gpd.read_file(r'intersects.shp')
intersectednew = intersectdata.to_crs(epsg=4326)

####Read in baseline layer 
baseline = gpd.read_file(r'transects.shp')
baseline = baseline.to_crs(epsg=4326)

####Errors 
measurementerror = 0.3
digitisingerror = 0



# intersected = transectstartlocator(baseline, intersectednew) 

# intersectednew  = cleaning(intersected)

# linearregressionrate(intersectednew)
# endpointrate(intersectednew, CRS, ellipsoidal)

# netshorelinemovement(intersectednew, CRS, ellipsoidal)

# masking()

# DEMofDifference()

# DODSubPlot()

# OldesttoNewestDOD()

# LimitofDetection()

NetVolumeChange()
