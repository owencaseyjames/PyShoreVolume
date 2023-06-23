#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 16:00:23 2023

@author: owenjames
"""

import qgis.core
import os
import glob
from os import walk
import osgeo 
import processing
from osgeo import gdal
from qgis.core import (QgsProject, QgsRasterLayer, 
                    QgsLayerTree, QgsLayerTreeGroup,
                    QgsLayerTreeLayer)

# Data Directory Path
dir_path = '---'

#File type
filetype = "*.asc"

#Path to data directory where SCA will be perfromed from
saved = "---"

#Contour height 
contourheight = ---

#CRS 
CRSystem = 'EPSG:4326'

####Merge DEM's in Each Folder. Each folder must contain DEM's from a shared date, with the folder name
### the dates of the data collection in the format 'YYYYMMDD'
for roots, subdirectory, files in os.walk(dir_path):
    for subdirectories in subdirectory: 
        subdpath = os.path.join(roots,subdirectories)
        print(subdpath)
        layers = glob.glob(subdpath +"/"+ filetype)
        processing.run('gdal:merge', {'INPUT':layers,'OUTPUT':subdpath+'.tif'})
 
##Create Contours - Need to define the MHWS or shoreline measurment point here.
for i in glob.glob(saved + "*.tif"):  
    mergedfile = i 
    processing.run("saga:contourlines", {'GRID':mergedfile, "VERTEX":0,'ZMIN':contourheight , \
'ZMAX':contourheight, 'CONTOUR':mergedfile+".shp"})  #

###Merge Vector Layers and save to folder
shapefiles = glob.glob(saved + '*.shp')
print(shapefiles)
processing.run('qgis:mergevectorlayers',{'LAYERS':shapefiles, 'CRS':QgsCoordinateReferenceSystem(CRSystem),'OUTPUT':saved+"MergedVector.shp"})