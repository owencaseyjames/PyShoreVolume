#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 18:55:10 2023

@author: owenjames
"""
# LinearRegressionRate.py

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

import sys

import Config

def linearregressionrate(intersectednew):
        val = min(intersectednew['TR_ID'])
        lrrdic = {}
        cols = []
        uniquetrans = intersectednew.TR_ID.unique()

        for e, ids in enumerate(uniquetrans):
               if val == e:     
         
                   s = GeoDataFrame(intersectednew.loc[intersectednew['TR_ID'] == ids])
                   
                   geomsx = np.array(s['geometry_x'].x)
                   geomsy = np.array(s['geometry_x'].y) 
                   
                   #Got the transect point geom
                   transgeometryx = np.array(s['X'])
                   transgeometryy = np.array(s['Y'])
                   years = np.array(s['layer'])
        
                   geoms = np.vstack((geomsx,geomsy)).T
                   transgeoms = np.vstack((transgeometryx, transgeometryy)).T
                   print(transgeoms[0][0],transgeoms[0][1])
        
                   ds = []
                   for i in geoms:             
                       ds.append(geopy.distance.geodesic((i[0],i[1]),(transgeoms[0][0],transgeoms[0][1])).m)
                   lrrdic[ids] = dict(zip(years, ds))                 
                   val = val+1    
                   #####Issue with newdate geoms - should remove duplicate date coords on one trans 
        
        
        lindf =   pd.DataFrame(lrrdic)  
        final = lindf.sort_index()
        linreg = linear_model.LinearRegression()
        lrrresults = {}
        for i in final.columns:
            findropna = pd.DataFrame()
            findropna['Distance from baseline'] = final[i].dropna(axis=0)
            if len(findropna.index) > 4:        
                ##Reg plots
                findropna['year']= findropna.index
                findropna['yearplot'] = pd.to_datetime(findropna['year'], format="%Y%m")
                # print(findropna['yearplot'])
                findropna['years'] = findropna['year'].astype('float64')
                # print(findropna)
                sns.regplot(data=findropna, x= 'years', y='Distance from baseline')
                plt.title("Transect %d" %i)
                plt.show()
                
                ###Reg results 
                
                finlist = np.array(findropna['year'])
                finlist.astype('float64')
                # print(finlist)
            
                yvals = findropna['Distance from baseline'].values.reshape(-1,1)
                xvals = finlist.reshape(-1,1)
                
                linfin = linreg.fit(xvals,yvals)
                ypred  = linfin.predict(xvals)
                linfin.score(xvals,yvals)
                resid = yvals - ypred
                meanres = np.mean(resid)
                print(i)
                
                ##Alternate stats model - results differ
                replaced=[]
                for ins in findropna['yearplot']:
                    replaced.append(ins.replace(tzinfo=timezone.utc).timestamp())
                # print(replaced)    
                Ysm = findropna['Distance from baseline']
                Xsm = replaced
                Xsm = sm.add_constant(Xsm)
                models = sm.OLS(Ysm, Xsm)
                results = models.fit()
                print(results.summary())        
                ##### 
                
                ###Results from first model.
                print('Coef:', linfin.coef_)
                print('Intercept:', linfin.intercept_)
                print("R 2:",r2_score(yvals,ypred))
                print('Residuals (mean should be zero):', meanres)
                
                lrrresults[i] = {'Coefficient': linfin.coef_,'Intercept':linfin.intercept_, \
                                  'R2':r2_score(yvals,ypred),'Mean of Residuals':meanres}
        
            else: 
                continue
            # break
        with open (Config.save_to_path+'/lrrdictionary.pkl', 'wb') as fb:
            pickle.dump(lrrresults, fb, protocol = pickle.HIGHEST_PROTOCOL)