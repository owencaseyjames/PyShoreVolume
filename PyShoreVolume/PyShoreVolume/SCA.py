#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 20:00:31 2023

@author: owenjames
"""
#SCA.py

    
from ShorelineChange.NSMEandA import NSMEandA 

from ShorelineChange.NSM import  NSM

from ShorelineChange.EPR import EPR 

from ShorelineChange.SCE import SCE 

from ShorelineChange.LRR import LRR 

            
class SCA():

    
            def __init__(self, transectplot, intersectednew, ellipsoidal, 
                         origCRS, save_to_path, measurementerror, 
                         georeferencingerror, distancemeasureerror,CRS):
                
                
                self.transectplot = transectplot
                self.origCRS = origCRS
                self.ellipsoidal = ellipsoidal
                self.measurementerror = measurementerror 
                self.georeferencingerror = georeferencingerror 
                self.distancemeasureerror = distancemeasureerror
                self.intersectednew = intersectednew 
                self.CRS = CRS
                self.save_to_path = save_to_path
                
            def EPR(self):
                 epr = EPR(self.intersectednew, self.CRS,self.save_to_path, self.measurementerror,
                     self.georeferencingerror, self.distancemeasureerror, self.origCRS, self.ellipsoidal)   
                 return epr
             
            def NSM(self):
                nsm = NSM(self.intersectednew, self.transectplot, self.CRS, self.origCRS,
                    self.ellipsoidal, self.save_to_path)
                return nsm
            
            def LRR(self):
                lrr = LRR(self.intersectednew, self.ellipsoidal, self.save_to_path)
                return lrr 
            
            def NSMEandA(self):
                nsmeanda = NSMEandA(self.intersectednew, self.transectplot, self.origCRS, self.CRS, 
                        self.ellipsoidal, self.save_to_path)
                return nsmeanda 
            
            def SCE(self):
                sce = SCE(self.intersectednew, self.transectplot, self.CRS, self.ellipsoidal, self.save_to_path)
                return sce
            
            
            
            