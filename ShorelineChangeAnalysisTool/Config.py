#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 18:00:41 2023

@author: owenjames
"""
#Config.py 

import sys 
import os


os.chdir('/Users/owenjames/Dropbox/PhD/Shoreline_Data/cco_data-20220625114304 Woola/data/lidar/')
path = '/Users/owenjames/Dropbox/PhD/Shoreline_Data/cco_data-20220625114304 Woola/data/lidar/'

sys.path.append(r'/Users/owenjames/Dropbox/PhD/Python_Scripts/ShorelineChangeAnalysisTool/')

###setting the PROJ_LIB proj.db variable to the rasterio PROJ folder
os.environ['PROJ_LIB'] = '/Users/owenjames/opt/anaconda3/envs/geo_env/lib/python3.6/site-packages/rasterio/proj_data/'

###Save to path 
directory = 'results/'
save_to_path = os.path.join(path, directory)
os.makedirs(save_to_path, exist_ok = True)
print(save_to_path)

##Define pixel size (m2)    
pixelsize = 1

