# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 12:47:02 2023

@author: bputra

This script is designed to plot all of the currently existing IG data 
in the "Pressure Data" folder. 
As inputs, it takes in CSV files that are copies of the "Untitled" part of the
TDMS file. Please display the "Time" data in the file in the format
"mm/dd/yyyy hh:mm:ss.000 AM/PM". 
This script also takes in .mat pressure files as inputs. 
If using .mat file for pressure, keep it as it is.
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

#%% Load pressure data from csv (from tdms)

#initialize file path for csv files
path = 'Pressure Data\*.csv'

#initialize empty dataframe
dfpcsv = pd.DataFrame()

#Loop over all csv files in folder and combine data into dataframe
for fname in glob.glob(path):
    tempdfp = pd.read_csv(fname)
    dfpcsv = pd.concat([dfpcsv, tempdfp], ignore_index=True)

#Convert time data into nicer format
for i in range(len(dfpcsv["Time"])):
    dfpcsv.iloc[i, 0] = dt.datetime.strptime(
        dfpcsv.iloc[i, 0],'%m/%d/20%y  %I:%M:%S.%f %p')
    
#Get rid of values when pressure is above ion gauge range
dfpcsv.loc[dfpcsv['Aprime ion gauge'] > 0.0001, 'Aprime ion gauge'] = np.nan
#%%% Load pressure data from .mat

#initialize file path for mat files
path = 'Pressure Data/*_IG_Pressures.mat'

#initialize empty dataframe
matdfp = pd.DataFrame()

#Loop over all mat files in folder and combine data into dataframe
for fname in glob.glob(path):
    print(fname)
    tempmat = loadmat(fname)
    time = np.transpose(tempmat['IG_Pressures_time'])
    pressures = np.transpose(tempmat['AP_IG_PRESSURE'])
   #minpressure = pressures.argmin()
    newData = list(zip(time, pressures))
    tempdfp = pd.DataFrame(data=newData, columns=['Time', 'Aprime ion gauge'])
    #Convert time data from epoch time to ISO format
    for i in range(len(tempdfp['Time'])):
        tempdfp.iloc[i, 0] = float(tempdfp.iloc[i, 0])
        tempdfp.iloc[i, 1] = float(tempdfp.iloc[i, 1])
        tempdfp.iloc[i, 0] = dt.datetime.utcfromtimestamp(
            tempdfp.iloc[i, 0]).replace(tzinfo=dt.timezone.utc)
        tempdfp.iloc[i, 0] = tempdfp.iloc[i, 0].astimezone(
            pytz.timezone('Etc/GMT+5'))
        tempdfp.iloc[i, 0] = tempdfp.iloc[i, 0].replace(tzinfo=None)
    matdfp = pd.concat([matdfp, tempdfp], ignore_index=True)

#Get rid of values when pressure is above ion gauge range
matdfp.loc[matdfp['Aprime ion gauge'] > 0.0001, 'Aprime ion gauge'] = np.nan
#%% Concatenate tdms and mat data
dfp = pd.concat([dfpcsv, matdfp], ignore_index=True)

#%% Redefine mat data as dfp
dfp = matdfp

#%%Convert IG data to log10
for i in range(len(dfp['Aprime ion gauge'])):
    dfp.iloc[i, 1] = np.log10(dfp.iloc[i, 1])
    
#%% Plotting

#Close all plots
plt.close('all')

fig, ax = plt.subplots()
#Plot
plt.plot(dfp['Time'], dfp['Aprime ion gauge'], marker='.')

#Set axis labels and legends
fmt = mdates.DateFormatter('%m/%d/%Y')

ax.xaxis.set_major_formatter(fmt)
#plt.gca().ticklabel_format(style='sci', scilimits=(0,0), axis='y')
ax.set_xlabel('Dates')
ax.set_ylabel('IG Pressure (log10(Torr))')
ax.set_title('Ion gauge pressure by date')
ax.axvspan(dfp.iloc[1,0],dfp.iloc[6,0], facecolor='r',alpha=0.1)
fig.autofmt_xdate()

fig.tight_layout()

plt.show()
