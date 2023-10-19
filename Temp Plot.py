# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 20:27:15 2023

@author: bputra

This script is designed to plot all of the currently existing thermistor data 
in the "Temperature Data" folder. 
This script takes in .mat temperature files as inputs.
"""

from scipy.io import loadmat
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import pytz
import glob
import os

#File path
os.chdir('C:/Users/bputra1/Documents/Scripts/HSX_Glow_Analysis')

#%%% Load temperature data from .mat

#initialize file path for mat files
path = 'Temperature Data/Bake Temps/*_Vessel_Temps.mat'

#initialize empty dataframe
dfT = pd.DataFrame()

#Loop over all mat files in folder and combine data into dataframe
stddev=[]
for fname in glob.glob(path):
    tempmat = loadmat(fname)
    del tempmat['__globals__']
    del tempmat['__header__']
    del tempmat['__version__']
    print(fname)
    for k, v in tempmat.items():
        tempmat[k]=np.transpose(v)
        tempmat[k]=tempmat[k].tolist()
        for j in range(len(tempmat[k])):
             tempmat[k][j]=float(tempmat[k][j][0])
    tempdfT = pd.DataFrame(data=tempmat)

#Convert time data from epoch time to ISO format+calculate std dev
    for i in range(len(tempdfT['Vessel_Temps_time'])):
        tempdfT.iloc[i, -1] = dt.datetime.utcfromtimestamp(
            tempdfT.iloc[i, -1]).replace(tzinfo=dt.timezone.utc)
        tempdfT.iloc[i, -1] = tempdfT.iloc[i, -1].astimezone(
            pytz.timezone('Etc/GMT+5'))
        tempdfT.iloc[i, -1] = tempdfT.iloc[i, -1].replace(tzinfo=None)
        stddev.append(tempdfT.iloc[i, 1:-1].std(axis=0, ddof=0))
    dfT = pd.concat([dfT, tempdfT], ignore_index=True)
    
#%% Plotting

#Close all plots
plt.close('all')

fig1,ax1 = plt.subplots()

#Plot mean temperatures
ax1.errorbar(dfT['Vessel_Temps_time'], dfT['MEAN_TEMP_C_SCALED'], yerr=stddev, 
             linestyle='None', marker='.', ms=1, ecolor='red')

#Set axis labels and legends
fmt = mdates.DateFormatter('%m/%d %H:%M')

ax1.xaxis.set_major_formatter(fmt)
#plt.gca().ticklabel_format(style='sci', scilimits=(0,0), axis='y')
ax1.set_xlabel('Dates')
ax1.set_ylabel('Temperature (degC))')
ax1.set_title('Vessel mean temperature by date')
fig1.autofmt_xdate()

fig1.tight_layout()
fig1.show()



