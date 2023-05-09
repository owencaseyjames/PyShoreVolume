#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 11:28:07 2023

@author: owenjames
"""
#DODSubPlot.py

################################################################
##########               DOD Sub Plots             #############
##### Creates one subplot of DOD of Differnce Models    ########
#####                                                   ########
#####                                                   ########
################################################################


import rasterio as rio
import rasterio.mask
from rasterio.plot import show

import glob

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.gridspec as gridspec
from mpl_toolkits.axisartist.axislines import Subplot 


from PIL import Image

                
def DODSubPlot(save_to_path, subplotcols):
    """
    Creates one single subplot figure of all Digital Elevation Models of
    Difference.
    
    Parameters
    -------
    save_to_path: Path to the results folder
    subplotcols: Columns to be in the results folder.

    Returns
    -------
    A combined subplot of elevation of difference models.

    """
    multiple_rasters = [sorted(glob.glob(save_to_path+'*DOD.png'))]
    num = (len(sorted(glob.glob(save_to_path+"*DOD.png"))))
    nums = num -1
    if (num % 2) == 0:
        print('fine')
    else:
        num = num + 1
    
    plt.figure(figsize=(20,15))
    for i in multiple_rasters:
        for count in range(0,len(multiple_rasters[0])):
         
                # #create figure
                
                pic = Image.open(i[count])
                fig = matplotlib.pyplot.figure(1)   
                plt.subplot(2, subplotcols, count+1)             
                plt.axis('off')
                plt.tight_layout()
                plt.imshow(pic)
                plt.savefig(save_to_path+'/'+'DOD Subplots.png',bbox_inches='tight')
  
                
def DODautumnsubplot(save_to_path, subplotcols):
    """
    Creates one single subplot figure of all Autumn to Autumn Digital Elevation Models of
    Difference.
    
    Parameters
    -------
    save_to_path: Path to the results folder

    Returns
    -------
    A combined subplot of elevation of difference models.
    """
    autumnresults = [sorted(glob.glob(save_to_path+"*autumn.png"))]
    
    num = (len(sorted(glob.glob(save_to_path+"*autumn.png")))-1) 
    plt.figure(figsize=(10,10))
      
    for i in autumnresults:
        for count in range(0,len(autumnresults[0])):

  
        # #create figure            
            pic = Image.open(i[count])
            fig = matplotlib.pyplot.figure(1)    
            # if num > 
            plt.subplot(1,subplotcols,count+1)          
            plt.axis('off')
            plt.tight_layout()
            plt.imshow(pic)
            plt.savefig(save_to_path+'/'+'DOD Autumn Subplots.png',bbox_inches='tight')
                    



def DODspringsubplot(save_to_path, subplotcols):
    """
    Creates one single subplot figure of all Spring to Spring Digital Elevation Models of
    Difference.
    
    Parameters
    -------
    save_to_path: Path to the results folder

    Returns
    -------
    A combined subplot of elevation of difference models.
    """
    springresults = [sorted(glob.glob(save_to_path+"*spring.png"))]
    
    num = (len(sorted(glob.glob(save_to_path+"*spring.png")))-1) 
    plt.figure(figsize=(10,10))
    
    
    for i in springresults:
        for count in range(0,len(springresults[0])):
    
        # #create figure
            # print(i)
            pic = Image.open(i[count])
            fig = matplotlib.pyplot.figure(1)
            plt.subplot(2,subplotcols, count+1)
            
            plt.axis('off')
            # plt.tight_layout()
            plt.imshow(pic)
            plt.subplots_adjust(hspace=0, wspace=0)
            plt.savefig(save_to_path+'/'+'DOD Spring Subplots.png',bbox_inches='tight')     
            
                    
def DODsummersubplot(save_to_path, subplotcols):
    """
    Creates one single subplot figure of all Summer to Summer Digital Elevation Models of
    Difference.
    
    Parameters
    -------
    save_to_path: Path to the results folder

    Returns
    -------
    A combined subplot of elevation of difference models.
    """
    summerresults = [sorted(glob.glob(save_to_path+"*summer.png"))]
    
    num = (len(sorted(glob.glob(save_to_path+"*summer.png")))-1) 
    plt.figure(figsize=(10,10))
    for i in summerresults:
        for count in range(0,len(summerresults[0])):
   
        # #create figure
            
            pic = Image.open(i[count])
            fig = matplotlib.pyplot.figure(1)
            plt.subplot(2,subplotcols,count+1)
            
            plt.axis('off')
            
            plt.imshow(pic)
            plt.tight_layout()
            plt.subplots_adjust(hspace=0, wspace=0)
            plt.savefig(save_to_path+'/'+'DOD Summer Subplots.png',bbox_inches='tight')                

def DODwintersubplot(save_to_path, subplotcols):
    """
    Creates one single subplot figure of all Winter to Winter Digital Elevation Models of
    Difference
    
    Parameters
    -------
    save_to_path: Path to the results folder

    Returns
    -------
    A combined subplot of elevation of difference models.
    """
    winterresults = [sorted(glob.glob(save_to_path+"*winter.png"))]
    
    num = (len(sorted(glob.glob(save_to_path+"*winter.png")))-1) 
    plt.figure(figsize=(10,10))
    for i in winterresults:
        for count in range(0,len(winterresults[0])):

        
        # #create figure
            pic = Image.open(i[count])
            fig = matplotlib.pyplot.figure(1)
            plt.subplot(2,subplotcols,count+1)
            
            plt.axis('off')
            
            plt.tight_layout()
            plt.imshow(pic)
            plt.subplots_adjust(hspace=0, wspace=0)
            plt.savefig(save_to_path+'/'+'DOD Winter Subplots.png',bbox_inches='tight')                        

                