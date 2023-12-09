#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pickle as pkl


def OceanographicPlot(save_to_path, SurveyDates, Volumes, Oceanographic, FigWidth, FigHeight, FontSize, LineWidth, SurveyDateLineWidth, AxLegendFontSize, AxTickParams, LegendLoc, BottomAxis, BeachVolumeName):
    """
    Plots panel time series graphs of Wave Direction, Wave Height, Wave Period , Survey Dates and Volumes produced in DOD functions. 
    Calculates monthly averages of each of the wave parameter and plots them. 
    Plots survey dates as dashed red line vertical in the time series. 
    
    Parameters
    ----------
    save_to_path : string
        results folder path
    SurveyDates : datetime64[ns]
        Date and time of dates. 
    Volumes : DataFrame Object 
        DF with volumes and dates
    Oceanographic : DataFrame object
        DataFrame with Period (s), Height (m), Direction (d), Date/Time(m)
    FigWidth : float/integer
        figure width
    FigHeight : float/integer
        Figure Height
    FontSize : float/integer
        Font size of plot. 
    LineWidth : float/integer
        Line width of oceanographic data
    SurveyDateLineWidth : float/integer
        Line width of survey date vertical line
    AxLegendFontSize : float/integer
        Legend font size
    AxTickParams : float/integer
        Axis font size
    LegendLoc : string
        Location of legend on volume plot eg 'upper right'
        see https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
    BottomAxis : float/integer
        Bottom axis font size
    BeachVolumeName : string
        Name put in bracket eg ['Saunton']

    Returns
    -------
    Oceanographic plot saved to results folder. 

    """
    
    
    
    Oceanographic['Monthly Average Wave Height (m)'] = Oceanographic.groupby(Oceanographic['Date/Time'].dt.to_period('M'))['Height(m)'].transform('mean')
    Oceanographic['Monthly Average Wave Period (s)'] = Oceanographic.groupby(Oceanographic['Date/Time'].dt.to_period('M'))['Period(s)'].transform('mean')
    Oceanographic['Monthly Average Direction (d)'] = Oceanographic.groupby(Oceanographic['Date/Time'].dt.to_period('M'))['Direction(d)'].transform('mean')
    
    fig=plt.figure(figsize=(FigWidth,FigHeight))
        
    ax1=fig.add_subplot(4,1,1)
    Oceanographic.plot(x='Date/Time',y= 'Height(m)', ax=ax1, linewidth = LineWidth, fontsize= FontSize)
    Oceanographic.plot(x='Date/Time',y= 'Monthly Average Wave Height (m)', ax=ax1)   
    ax1.vlines(x = SurveyDates['Date/Time'],  
               ymax = Oceanographic['Height(m)'].max(),ymin =0, color='red',linestyle='dashed', linewidth = SurveyDateLineWidth)
    ax1.legend(fontsize = AxLegendFontSize)
    ax1.grid(True, which='major', linewidth=0.25)
    ax1.set_ylabel('Height (m)', fontsize = 9)
    ax1.axes.xaxis.set_ticklabels([])
    ax1.tick_params(bottom = False, labelsize=AxTickParams)
    ax1.set(xlabel=None)
    
    ax2=fig.add_subplot(4,1,2)
    Oceanographic.plot(x='Date/Time',y='Period(s)', ax=ax2, linewidth = LineWidth, fontsize= FontSize)
    Oceanographic.plot(x='Date/Time',y= 'Monthly Average Wave Period (s)', ax=ax2)
    ax2.vlines(x = SurveyDates['Date/Time'],  
               ymax = Oceanographic['Period(s)'].max(),ymin =0, color='red',linestyle='dashed', linewidth = SurveyDateLineWidth)
    ax2.legend(fontsize = AxLegendFontSize,loc= LegendLoc)
    ax2.axes.xaxis.set_ticklabels([])
    ax2.tick_params(bottom = False, labelsize=AxTickParams)
    ax2.set(xlabel=None)
    ax2.grid(True, which='major', linewidth=0.25)
    ax2.set_ylabel('Period (s)', fontsize = 9)
           
    ax3=fig.add_subplot(4,1,3)
    Oceanographic.plot(x='Date/Time',y='Direction(d)', ax=ax3, linewidth = LineWidth, fontsize= FontSize)
    Oceanographic.plot(x='Date/Time',y= 'Monthly Average Direction (d)', ax=ax3)
    # cleaned.plot(x='Date/Time(GMT)',y= 'Period Average Direction (d)', ax=ax3)
    ax3.vlines(x = SurveyDates['Date/Time'],  
               ymax = Oceanographic['Direction(d)'].max(),ymin =0, color='red',linestyle='dashed', linewidth = SurveyDateLineWidth)
    ax3.legend(fontsize = 9, loc= 'lower left')
    ax3.axes.xaxis.set_ticklabels([])
    ax3.tick_params(bottom = False, labelsize=AxTickParams)
    ax3.set(xlabel=None)
    ax3.grid(True, which='major', linewidth=0.25)
    ax3.set_ylabel('Direction (d)', fontsize =9)
           
    ax4 = fig.add_subplot(4,1,4)
    ax4.scatter(x = Volumes['Date'],y=Volumes['Volumes'])
    # ax4.scatter(x = Volumes['Date/Time(GMT)'],y=Volumes['Northam'])
    ax4.vlines(x = SurveyDates['Date/Time'],  
               ymax = 0,ymin = 0)
    ax4.legend(BeachVolumeName, fontsize= AxLegendFontSize, loc = LegendLoc)
    ax4.grid(True, which='major', linewidth=0.25)
    ax4.tick_params(labelsize = AxTickParams)
    ax4.set_ylabel('Volume Changes (m3)', fontsize =9)
    ax4.set_xlabel('Date', fontsize = BottomAxis)

    plt.tight_layout()
    plt.savefig(save_to_path+'Waveseries.jpg')
    
    