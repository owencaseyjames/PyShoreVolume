#DataImportandTransectDefinition.py>
import PyShoreVolume 
from  PyShoreVolume.CleanandTransectLocator.DataCleaning import cleaning
from PyShoreVolume.CleanandTransectLocator.TransectDefinition import transectstartlocator2, transectstartlocator1
import os
import geopandas as gpd


##Directories ** Dont forget '/' at the end
#os.chdir('/Users/owenjames/Dropbox/PhD/Shoreline_Data/cco_data-20220625114304/data/lidar/')
#path = '/Users/owenjames/Dropbox/PhD/Shoreline_Data/cco_data-20220625114304/data/lidar/'

###!!! NEEED TO STATE IN DESCRIPTION THE 

class DataImportandTransectDefinition(): 

    ###Save to path 
    
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
        self.intersects = cleaning(self.intersects)
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
    
    
#Extending amount of coordinates 
# gpd.options.display_precision = 10

# ##Desired CRS (Used in geopy measurements - go to site to find most suitable)
# CRS = 4277
# ##Specify the crs ellipsoid (Used in geopy distance measurements - go to site to find mathing ellipsoid for crs)
# ellipsoidal = 'Airy (1830)'




##Read in intersects shapefile 
# intersectdata = gpd.read_file(r'intersects.shp')
# intersectednew = intersectdata.to_crs(epsg=CRS)

# ###Review data
# print(intersectednew.columns)

# ####Read in baseline layer 

# print(baseline['geometry'])

# ####Errors 
# measurementerror = 0.3
# digitisingerror = 0


###Add transect points to geodataframe (X AND Y are transect root coord from the linestring) Number 1
###If wrong way around the erosion and accretion values  will be the wrong way around. Baseline m
# def transectstartlocator(baseline):
#         x = []
#         y = []
#         trid = []
#         val = 0
#         for i in baseline['geometry']:
#             # print(baseline['geometry'][val].coords[0])
#             x.append(baseline['geometry'][val].coords[1][0])
#             y.append(baseline['geometry'][val].coords[1][1])
#             trid.append(baseline['TR_ID'][val])
#             val = val + 1
#         transectgeoms = GeoDataFrame({'X':x,'Y':y,'TR_ID':trid})
#         transectgeoms = GeoDataFrame(transectgeoms, geometry=gpd.points_from_xy(transectgeoms.X,transectgeoms.Y))
#         intersected = intersectednew.merge(transectgeoms, on='TR_ID', how= 'left')

# # #Plot to review transect baselines
#         transectgeoms.plot()
#         intersected = intersected.set_geometry('geometry_x')
# # transectgeoms.plot()
# ### Number 2
# ##If transect and thus baseline start locations are on the other sifde of the transect 
# def transectstartlocator2(baseline):
#         x = []
#         y = []
#         trid = []
#         val = 0
#         for i in baseline['geometry']:
#             # print(baseline['geometry'][val].coords[0])
#             x.append(baseline['geometry'][val].coords[0][0])
#             y.append(baseline['geometry'][val].coords[0][1])
#             trid.append(baseline['TR_ID'][val])
#             val = val + 1
#         transectgeoms = GeoDataFrame({'X':x,'Y':y,'TR_ID':trid})
#         transectgeoms = GeoDataFrame(transectgeoms, geometry=gpd.points_from_xy(transectgeoms.X,transectgeoms.Y))
#         intersected = intersectednew.merge(transectgeoms, on='TR_ID', how= 'left')

# # #Plot to review transect baselines
#         transectgeoms.plot()
#         intersected = intersected.set_geometry('geometry_x')
        

# ###Set geometry column now that Geometry x is the coords of the intersected point
# intersected = intersected.set_geometry('geometry_x')

###Extract the intersections of contours produced from errors
# lowerranges = GeoDataFrame(intersected.loc[intersected['Z']== intersected['Z'].min()])
# lowerranges = lowerranges.set_geometry('geometry_x')


# higherranges = intersected.loc[intersected['Z']== intersected['Z'].max()]
# # higherranges['TR_ID'] = higherranges['TR_ID'].astype(int)
# # higher = GeoDataFrame(intersectednew.loc[intersectednew['Z']== intersectednew['Z'].max()])
# higherranges= higherranges.set_geometry('geometry_x')
# print(max(higherranges['TR_ID']))
# print(max(lowerranges['TR_ID']))
# highers.TR_ID.dtype

