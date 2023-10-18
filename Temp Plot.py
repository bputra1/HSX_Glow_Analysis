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
os.chdir('C:/Users/Asus/Desktop/Work/HSX/Glow Data')

#%%% Load temperature data from .mat

#initialize file path for mat files
path = 'Temperature Data/*_Vessel_Temps.mat'

#initialize empty dataframe
dfT = pd.DataFrame()

#Loop over all mat files in folder and combine data into dataframe
for fname in glob.glob(path):
    tempmat = loadmat(fname)
    print(fname)
    time = np.transpose(tempmat['Vessel_Temps_time'])
    temps = np.transpose(tempmat['MEAN_TEMP_C_SCALED'])
    newData = list(zip(time, temps))
    tempdfT = pd.DataFrame(data=newData, columns=['Time', 'Mean Temps'])
    #Convert time data from epoch time to ISO format
    for i in range(len(tempdfT['Time'])):
        tempdfT.iloc[i, 0] = float(tempdfT.iloc[i, 0])
        tempdfT.iloc[i, 1] = float(tempdfT.iloc[i, 1])
        tempdfT.iloc[i, 0] = dt.datetime.utcfromtimestamp(
            tempdfT.iloc[i, 0]).replace(tzinfo=dt.timezone.utc)
        tempdfT.iloc[i, 0] = tempdfT.iloc[i, 0].astimezone(
            pytz.timezone('Etc/GMT+5'))
        tempdfT.iloc[i, 0] = tempdfT.iloc[i, 0].replace(tzinfo=None)
    dfT = pd.concat([dfT, tempdfT], ignore_index=True)
    
#%% Plotting

#Close all plots
plt.close('all')

#Plot
plt.scatter(dfT['Time'], dfT['Mean Temps'], marker='.')

#Set axis labels and legends
fmt = mdates.DateFormatter('%m/%d/%Y')

plt.gca().xaxis.set_major_formatter(fmt)
#plt.gca().ticklabel_format(style='sci', scilimits=(0,0), axis='y')
plt.xlabel('Dates')
plt.ylabel('Temperature (degC))')
plt.title('Vessel mean temperature by date')
plt.gcf().autofmt_xdate()

plt.gcf().tight_layout()
plt.show()