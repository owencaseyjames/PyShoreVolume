#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 12:54:50 2023

@author: owenjames
"""

#DOD.py 

from VolumeChanges import DEMofDifference

from VolumeChanges import DODSubPlot
# from DODSubPlot import DODautumnsubplot, DODwintersubplot, DODspringsubplot, DODsummersubplot

from VolumeChanges import LimitofDetection

from VolumeChanges import MaskingDEM
# from MaskingDEM import masking

from VolumeChanges import NetVolumeChange

from VolumeChanges import OldesttoNewest

from VolumeChanges import SeasonalDOD
from VolumeChanges import winterDOD, springDOD, summerDOD, autumnDOD

class DOD():
    
            def __init__(self, subplotcols, titlesize, pixelsize, 
                         DODCRS, figwidth, figheight,
                         save_to_path, path, MaskingCRS, measurementerror):
                
                self.subplotcols = subplotcols 
                self.titlesize = titlesize 
                self.pixelsize = pixelsize
                self.DODCRS = DODCRS
                self.figwidth = figwidth 
                self.figheight = figheight
                self.save_to_path = save_to_path
                self.path = path
                self.MaskingCRS = MaskingCRS
                self.measurementerror = measurementerror
           
            def Masking(self):
                MaskingDEM(self.path, self.MaskingCRS, self.DODCRS)
            
            def DEMofDifference(self):
                dodres = DEMofDifference(self.path, self.DODCRS, self.save_to_path, self.pixelsize)
                return dodres
             #Isthereawaytocallsuplotsextensionsfromthesubplot as part of this method.
            def DODSubPlot(self):
                DODSubPlot(self.save_to_path, self.subplotcols)
           
            def winterDOD(self):
                dodres = winterDOD(self.path, self.pixelsize, self.save_to_path, self.DODCRS)
                return dodres
            
            def summerDOD(self):
                dodres = summerDOD(self.path, self.pixelsize, self.save_to_path, self.DODCRS)            # def 
                return dodres
            
            def autumnDOD(self):
                dodres = autumnDOD(self.path, self.pixelsize, self.save_to_path, self.DODCRS)                
                return dodres
            
            def springDOD(self):
                dodres = springDOD(self.path, self.pixelsize, self.save_to_path, self.DODCRS)
                return dodres

            def DODautumnsubplot(self):
                DODautumnsubplot(self.save_to_path)
                
            def DODspringsubplot(self):
                DODspringsubplot(self.save_to_path)
                
            def DODsummersubplot(self):
                DODsummersubplot(self.save_to_path)                
                
            def DODwintersubplot(self):
                DODwintersubplot(self.save_to_path)         
            
            def NetVolumeChange(self):
                netvol = NetVolumeChange(self.path, self.pixelsize, self.measurementerror)
                return netvol
           
            def OldesttoNewest(self):
                OldesttoNewest(self.path, self.save_to_path, self.DODCRS)
                
          
                       