# -*- coding: utf-8 -*-
"""
Created on Mon May  1 14:03:12 2023

@author: bputra

This script is designed to plot PvT data from the RGA, pressure data, and glow
current. 
Required inputs: 
For RGA part, CSV file with columns labeled Time(s) and names of mass numbers
of interest.
For pressure part, CSV file with the "Untitled" part of the TDMS file. Please 
display the "Time" data in the file in the format "mm/dd/yyyy hh:mm:ss.000 AM/PM".
If using .mat file for pressure, keep it as it is.
For glow current, CSV file from LJLogUD with Times(s), A, B, C, and D as headers.

Keep the paths to these input files in mind.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import pytz
import os
from scipy.io import loadmat
import glob

#Functions:
def round_seconds(obj: dt.datetime) -> dt.datetime:
    if obj.microsecond >= 500_000:
        obj += dt.timedelta(seconds=1)
    return obj.replace(microsecond=0)

#Close all open plots
plt.close('all')

#File path
os.chdir('C:/Users/bputra1/Documents/Scripts/HSX_Glow_Analysis')

#Input start time from RGA PVT file
starttime = dt.datetime.fromisoformat('2023-09-29 04:54:15')

#Working gas
workinggas = "Water"

#%%Import your RGA data from csv file in same directory as program
datfile = 'RGA Data\Bake_20230929_PVT.csv'
dfRGA = pd.read_csv(datfile)
for i in range(len(dfRGA["Time(s)"])):
    dfRGA.iloc[i, 0] = starttime+dt.timedelta(
        seconds=dfRGA.iloc[i, 0])
    dfRGA.iloc[i, 0] = round_seconds(dfRGA.iloc[i, 0])
dfRGA = dfRGA.loc[:, ~dfRGA.columns.str.contains('^Unnamed')]
#dfRGA = dfRGA.loc[19471:]

#%%Import pressure data (csv from tdms)
datfile = 'Pressure Data\pressure_20230511.csv'
dfp = pd.read_csv(datfile, index_col='Aprime foreline convectron_Time*')
for i in range(len(dfp["Time"])):
    dfp.iloc[i, 0] = round_seconds(dt.datetime.strptime(
        dfp.iloc[i, 0],'%m/%d/20%y  %I:%M:%S.%f %p'))
    if dfp.iloc[i, 0]==starttime or (
        dfp.iloc[i, 0]==starttime+dt.timedelta(seconds=1)):
        istart = i
    if dfp.iloc[i, 0]==dfRGA.iloc[-1, 0] or dfp.iloc[i, 0]==(
            dfRGA.iloc[-1, 0]+dt.timedelta(seconds=1)):
        iend = i
pdata = dfp["Aprime tank convectron"]
#istart = 8662
#%%Import pressure data (mat)
datfile = 'Pressure Data/2023_06_28_Vacuum_Pressures.mat'
pressures = loadmat(datfile)
ptime = np.transpose(pressures['Vacuum_Pressures_time'])
ConvAp = np.transpose(pressures['AP_TANK_PRESSURE'])
dfp1 = pd.DataFrame(data=list(
    zip(ptime, ConvAp)), columns=['Time', 'Aprime tank convectron'])

#for multiple days
datfile = 'Pressure Data/2023_06_15_Vacuum_Pressures.mat'
pressures = loadmat(datfile)
ptime = np.transpose(pressures['Vacuum_Pressures_time'])
ConvAp = np.transpose(pressures['AP_TANK_PRESSURE'])
dfp2 = pd.DataFrame(data=list(
    zip(ptime, ConvAp)), columns=['Time', 'Aprime tank convectron'])
dfp = pd.concat([dfp1, dfp2], ignore_index=True)

for i in range(len(dfp["Time"])):
    dfp.iloc[i, 0] = float(dfp.iloc[i,0])
    dfp.iloc[i, 0] = dt.datetime.utcfromtimestamp(
        dfp.iloc[i, 0]).replace(tzinfo=dt.timezone.utc)
    dfp.iloc[i, 0] = dfp.iloc[i, 0].astimezone(
        pytz.timezone('Etc/GMT+5'))
    dfp.iloc[i, 0] = dfp.iloc[i, 0].replace(tzinfo=None)
    if dfp.iloc[i, 0]==starttime or (
        dfp.iloc[i, 0]==starttime+dt.timedelta(seconds=1)):
        istart = i
    if dfp.iloc[i, 0]==dfRGA.iloc[-1, 0] or dfp.iloc[i, 0]==(
            dfRGA.iloc[-1, 0]+dt.timedelta(seconds=1)):
        iend = i
istart = 936

#Get rid of values when pressure is above convectron gauge range
dfp.loc[dfp['Aprime tank convectron'] > 850, 'Aprime tank convectron'] = np.nan

pdata = dfp["Aprime tank convectron"]

#%% Import ion gauge data
datfile = 'Pressure Data/2023_07_05_IG_Pressures.mat'
pressures = loadmat(datfile)
ptime = np.transpose(pressures['IG_Pressures_time'])
IGAp = np.transpose(pressures['AP_IG_PRESSURE'])
dfIG = pd.DataFrame(data=list(
    zip(ptime, IGAp)), columns=['Time', 'Aprime ion gauge'])

# #for multiple days
# datfile = 'Pressure Data/2023_06_29_IG_Pressures.mat'
# pressures = loadmat(datfile)
# ptime = np.transpose(pressures['IG_Pressures_time'])
# IGAp = np.transpose(pressures['AP_IG_PRESSURE'])
# dfIG2 = pd.DataFrame(data=list(
#     zip(ptime, IGAp)), columns=['Time', 'Aprime ion gauge'])

# datfile = 'Pressure Data/2023_06_30_IG_Pressures.mat'
# pressures = loadmat(datfile)
# ptime = np.transpose(pressures['IG_Pressures_time'])
# IGAp = np.transpose(pressures['AP_IG_PRESSURE'])
# dfIG3 = pd.DataFrame(data=list(
#     zip(ptime, IGAp)), columns=['Time', 'Aprime ion gauge'])

# dfIG = pd.concat([dfIG1, dfIG2, dfIG3], ignore_index=True)

for k in range(len(dfIG["Time"])):
    dfIG.iloc[k, 0] = float(dfIG.iloc[k,0])
    dfIG.iloc[k, 0] = dt.datetime.utcfromtimestamp(
        dfIG.iloc[k, 0]).replace(tzinfo=dt.timezone.utc)
    dfIG.iloc[k, 0] = dfIG.iloc[k, 0].astimezone(
        pytz.timezone('Etc/GMT+5'))
    dfIG.iloc[k, 0] = dfIG.iloc[k, 0].replace(tzinfo=None)
    
dfIG.loc[dfIG['Aprime ion gauge'] > 0.0001, 'Aprime ion gauge'] = np.nan
IGdata = dfIG['Aprime ion gauge']
#%%Import current data
datfile = 'Current Data\GDC_Voltages_20230511.csv'
dfc = pd.read_csv(datfile)
#Replace epoch time with ISO format time; pay attention to timezone
#Also, LabJack time is 66 years off, so replace it with current year
for t in range(len(dfc['Time(s)'])):
    dfc.iloc[t, 0] = dt.datetime.utcfromtimestamp(
        dfc.iloc[t, 0]).replace(tzinfo=dt.timezone.utc)
    dfc.iloc[t, 0] = dfc.iloc[t, 0].astimezone(
        pytz.timezone('Etc/GMT+5'))
    dfc.iloc[t, 0] = dfc.iloc[t, 0].replace(year=2023)
    dfc.iloc[t, 0] = dfc.iloc[t, 0].replace(tzinfo=None)
    if round_seconds(dfc.iloc[t, 0])==starttime or round_seconds(
                (dfc.iloc[t, 0]))+dt.timedelta(seconds=1)==starttime:
        tstart = t
    if round_seconds(dfc.iloc[t, 0])==dfRGA.iloc[-1, 0] or round_seconds(
            dfc.iloc[t, 0])==(dfRGA.iloc[-1, 0]+dt.timedelta(seconds=1)):
        tend = t
    else:
        tend = len(dfc['Time(s)'])
#Scale voltage data by -500 and divide by 250 ohms
for (columnName, columnData) in dfc.items():
    if columnName == "Time(s)":
        continue
    dfc[columnName] = (columnData*(-500))/250

#Add total and mean current to dataframe
totalcurrent = []
meancurrent = []
for t in range(len(dfc['Time(s)'])):
    totalcurrent.append(
        dfc.iloc[t, 1] + dfc.iloc[t, 2] + dfc.iloc[t, 3] + dfc.iloc[t, 4])
    meancurrent.append(np.average(
        [dfc.iloc[t,1], dfc.iloc[t,2], dfc.iloc[t,3], dfc.iloc[t,4]]))
dfc['Total Current'] = totalcurrent
dfc['Average Current'] = meancurrent

#Replace individual quadrant data with difference from mean
for t in range(len(dfc['Time(s)'])):
    for i in range(1, 5):
        dfc.iloc[t, i] = np.abs(dfc.iloc[t, i] - dfc.iloc[t, 6])

#%% Import temperature data

#initialize file path for mat files
path = 'Temperature Data/Bake Temps/*_Vessel_Temps.mat'

#initialize empty dataframe
dfT = pd.DataFrame()

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
# datfile = 'Temperature Data/2023_09_05_Vessel_Temps.mat'
# temps = loadmat(datfile)
# Ttime = np.transpose(temps['Vessel_Temps_time'])
# meantemp = np.transpose(temps['MEAN_TEMP_C_SCALED'])
# dfT = pd.DataFrame(data=list(
#     zip(Ttime, meantemp)), columns=['Time', 'Temp'])    

# #for multiple days
# datfile = 'Temperature Data/2023_06_29_Vessel_Temps.mat'
# temps = loadmat(datfile)
# Ttime = np.transpose(temps['Vessel_Temps_time'])
# meantemp = np.transpose(temps['MEAN_TEMP_C_SCALED'])
# dfT2 = pd.DataFrame(data=list(
#     zip(Ttime, meantemp)), columns=['Time', 'Temp'])    

# datfile = 'Temperature Data/2023_06_30_Vessel_Temps.mat'
# temps = loadmat(datfile)
# Ttime = np.transpose(temps['Vessel_Temps_time'])
# meantemp = np.transpose(temps['MEAN_TEMP_C_SCALED'])
# dfT3 = pd.DataFrame(data=list(
#     zip(Ttime, meantemp)), columns=['Time', 'Temp'])  

# dfT = pd.concat([dfT1, dfT2, dfT3], ignore_index=True)

# for k in range(len(dfT["Time"])):
#     dfT.iloc[k, 0] = float(dfT.iloc[k,0])
#     dfT.iloc[k, 0] = dt.datetime.utcfromtimestamp(
#         dfT.iloc[k, 0]).replace(tzinfo=dt.timezone.utc)
#     dfT.iloc[k, 0] = dfT.iloc[k, 0].astimezone(
#         pytz.timezone('Etc/GMT+5'))
#     dfT.iloc[k, 0] = dfT.iloc[k, 0].replace(tzinfo=None)
    
Tdata = dfT['Mean Temps']
#%% Plotting    
plt.close('all')
#Generate figure and subplot
fig = plt.figure(figsize=(6,8))
ax1 = fig.add_subplot(511)
ax2 = fig.add_subplot(512, sharex=ax1)
ax3 = fig.add_subplot(513, sharex=ax1)
ax4 = fig.add_subplot(514, sharex=ax1)
ax5 = fig.add_subplot(515, sharex=ax1)
# ax6 = fig.add_subplot(616, sharex=ax1)
# ax7 = fig.add_subplot(717, sharex=ax1)

#set the color_cylce to make colors different across subplots
color_cycle = plt.rcParams['axes.prop_cycle']()

#Plot the raw data for each mass number
for (columnName, columnData), cc in zip(dfRGA.items(), color_cycle):
    if columnName == "Time(s)":
        continue
    if columnName == workinggas:
        ax1.plot(dfRGA["Time(s)"], columnData, label=str(columnName),**cc)
    elif columnName in {"Hydrogen"}:
        ax2.plot(dfRGA["Time(s)"], columnData, label=str(columnName),**cc)
    elif columnName in {"Oxygen", "Water", "Nitrogen"}: 
        ax3.plot(dfRGA["Time(s)"], columnData, label=str(columnName),**cc)
    elif columnName in {"Helium","Carbon dioxide", "Carbon", "Carbon Dioxide", "Argon"}:
        ax4.plot(dfRGA["Time(s)"], columnData, label=str(columnName),**cc)

#plot pressure data
# ax5.plot(dfp["Time"].iloc[istart:iend], pdata[istart:iend])

# #plot IG data
# ax5.plot(dfIG["Time"], IGdata)

#Plot current data
# for (columnName, columnData) in dfc.items():
#     if columnName not in ('A','B','C','D'):
#         continue
#     ax6.plot(dfc["Time(s)"], columnData, label=str(columnName))
# ax7.plot(dfc['Time(s)'], dfc['Total Current'], label='Total Current')
# ax7.plot(dfc['Time(s)'], dfc['Average Current'], label='Average Current')

#plot temperature data
ax5.plot(dfT["Time"], Tdata, linestyle='None',marker='.',ms=1)

#Set axis labels and legends
fmt = mdates.DateFormatter('%m/%d %H:%M')

ax1.xaxis.set_major_formatter(fmt)
ax1.set_ylabel("Pressure(Torr)")
ax1.ticklabel_format(style='sci', scilimits=(0,0), axis='y')
ax1.legend(loc='center left', bbox_to_anchor=(1,0.5))

ax2.xaxis.set_major_formatter(fmt)
ax2.set_ylabel("Pressure(Torr)")
ax2.legend(loc='center left', bbox_to_anchor=(1,0.5))

ax3.xaxis.set_major_formatter(fmt)
ax3.set_ylabel("Pressure(Torr)")
ax3.legend(loc='center left', bbox_to_anchor=(1,0.5))

ax4.xaxis.set_major_formatter(fmt)
ax4.set_ylabel("Pressure(Torr)")
ax4.legend(loc='center left', bbox_to_anchor=(1,0.5))

# ax5.xaxis.set_major_formatter(fmt)
# ax5.set_ylabel("Pressure(Torr)")
# ax5.ticklabel_format(style='sci', scilimits=(0,0), axis='y')
# ax5.set_title("Convectron Pressure")

# ax5.xaxis.set_major_formatter(fmt)
# ax5.set_ylabel("Pressure(Torr)")
# ax5.ticklabel_format(style='sci', scilimits=(0,0), axis='y')
# ax5.set_title("IG Pressure")

# ax6.xaxis.set_major_formatter(fmt)
# ax6.set_xlabel("Time(s)")
# ax6.set_ylabel("Pressure(Torr)")
# ax6.set_title("IG Pressure")

ax5.xaxis.set_major_formatter(fmt)
ax5.set_xlabel("Time(s)")
ax5.set_ylabel("Temperature ($^{\circ}$C)")
ax5.set_title("Mean Vessel Temperature")

# ax6.xaxis.set_major_formatter(fmt)
# ax6.set_ylabel("Current(A)")
# ax6.set_title("Glow Current (Difference from Mean)")
# ax6.legend(loc='center left', bbox_to_anchor=(1,0.5))

# ax7.xaxis.set_major_formatter(fmt)
# ax7.set_xlabel("Time(s)")
# ax7.set_ylabel("Current(A)")
# ax7.set_title("Total and Average Glow Current")
# ax7.legend(loc='center left', bbox_to_anchor=(1,0.5))

fig.tight_layout()
fig.autofmt_xdate()
plt.show()







