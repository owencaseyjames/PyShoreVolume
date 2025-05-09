#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 20:00:31 2023

@author: owenjames
"""
#SCA.py
import os

import PyShoreVolume
from PyShoreVolume.ShorelineChange.NSMEandA import NSMEandA 

from PyShoreVolume.ShorelineChange.NSM import  NSM

from PyShoreVolume.ShorelineChange.EPR import EPR 

from PyShoreVolume.ShorelineChange.SCE import SCE 

from PyShoreVolume.ShorelineChange.LRR import LRR 

            
class SCA():

    
            def __init__(self, transectplot, intersectednew, ellipsoidal, 
                         save_to_path, CRS,  measurementerror, georeferencingerror,
                         distancemeasureerror, intersect_crs):
                
                
                self.transectplot = transectplot
                self.ellipsoidal = ellipsoidal
                self.intersectednew = intersectednew 
                self.CRS = CRS
                self.save_to_path = save_to_path
                self.intersect_crs = intersect_crs
                
                
            def EPR(self):
                 epr = EPR(self.intersectednew, self.CRS,self.save_to_path, self.ellipsoidal, self.intersect_crs)   
                 return epr
             
            def NSM(self):
                nsm = NSM(self.intersectednew, self.transectplot, self.CRS,
                    self.ellipsoidal, self.save_to_path, self.intersect_crs)
                return nsm
            
            def LRR(self):
                lrr = LRR(self.intersectednew, self.ellipsoidal, self.save_to_path)
                return lrr 
            
            def NSMEandA(self):
                nsmeanda = NSMEandA(self.intersectednew, self.transectplot, self.CRS, 
                        self.ellipsoidal, self.save_to_path, self.intersect_crs)
                return nsmeanda 
            
            def SCE(self):
                sce = SCE(self.intersectednew, self.transectplot, self.CRS, self.ellipsoidal, self.save_to_path, self.intersect_crs)
                return sce
            
            
            
            