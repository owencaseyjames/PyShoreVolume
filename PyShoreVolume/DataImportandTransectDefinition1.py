#DataImportandTransectDefinition.py>
import PyShoreVolume 
from  PyShoreVolume.CleanandTransectLocator.DataCleaning import cleaning
from PyShoreVolume.CleanandTransectLocator.TransectDefinition import transectstartlocator2, transectstartlocator1

import os

import geopandas as gpd

class DataImportandTransectDefinition(): 

    
    def __init__(self, CRS, intersects, transects, path, measurementerror, georeferror):
        
        self.CRS = CRS
        self.intersects = intersects
        self.transects = transects
        self.path = path
        self.measurementerror = measurementerror
        self.georeferror = georeferror 
        

    def transectstartlocator1(self):
        self.intersects = transectstartlocator1(self.transects, self.intersects)
        return self.intersects
        
    def transectstartlocator2(self):
        self.intersects = transectstartlocator2(self.transects, self.intersects)
        return self.intersects
    
    def cleaning(self):
        self.intersects = cleaning(self.intersects, self.CRS)
        return self.intersects
    
    def results(self):
        directory = 'results/'
        save_to_path = os.path.join(self.path, directory)  
        return save_to_path
    
    def errors(self):
        uniques = gpd.GeoDataFrame()
        uniques['layer'] = gpd.GeoDataFrame(self.intersects['layer'].unique())
        uniques = uniques.sort_values(by = ['layer'])
        uniques['Georef Err'] = self.georeferror
        uniques['Measurement Err'] = self.measurementerror
        if 'Georef Err' in self.intersects.columns: 
            uniques.set_index('layer').combine_first(self.intersects.set_index('layer'))            
        else:    
            self.intersects = self.intersects.merge(uniques, on='layer', how= 'left')   
        self.intersects = self.intersects.set_geometry('geometry_x')
        return self.intersects
    

