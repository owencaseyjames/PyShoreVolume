#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 18:00:41 2023

@author: owenjames
"""
#Config.py 

import os
import sys

"""
Sets Configuration Paramters

"""

os.chdir('/Users/owenjames/Dropbox/PhD/Shoreline_Data/cco_data-20220629141819 -WWH2/No/data/lidar/')
path = '/Users/owenjames/Dropbox/PhD/Shoreline_Data/cco_data-20220629141819 -WWH2/No/data/lidar/'

sys.path.append(r'/Users/owenjames/Dropbox/PhD/Python_Scripts/ShorelineChangeAnalysisTool/')

###setting the PROJ_LIB proj.db variable to the rasterio PROJ folder
# os.environ['PROJ_LIB'] = '/Users/owenjames/opt/anaconda3/envs/geo_env/lib/python3.6/site-packages/rasterio/proj_data/'

###Save to path 
directory = 'results/'
save_to_path = os.path.join(path, directory)
os.makedirs(save_to_path, exist_ok = True)
print(save_to_path)

##Define pixel size (m2)    
pixelsize = 1

##Desired CRS (Used in geopy measurements - go to site to find most suitable (27700 not available for SCA)
CRS = 4326

##Specify the crs ellipsoid (Used in geopy distance measurements - go to site to find mathing ellipsoid for crs)
ellipsoidal = 'Airy (1830)'

###Define margin of datasets
measurementerror = 0.15
georeferencingerror = 0 
distancemeasureerror = 0