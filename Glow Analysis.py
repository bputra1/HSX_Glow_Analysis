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

#Functions:
def round_seconds(obj: dt.datetime) -> dt.datetime:
    if obj.microsecond >= 500_000:
        obj += dt.timedelta(seconds=1)
    return obj.replace(microsecond=0)

#Close all open plots
plt.close('all')

#File path
os.chdir('C:/Users/Asus/Desktop/Work/HSX/Glow Data')

#Input start time from RGA PVT file
starttime = dt.datetime.fromisoformat('2023-06-08 09:53:00')

#Working gas
workinggas = "Water"

#%%Import your RGA data from csv file in same directory as program
datfile = 'RGA Data\Bake_20230608_PVT.csv'
dfRGA = pd.read_csv(datfile)
for i in range(len(dfRGA["Time(s)"])):
    dfRGA.iloc[i, 0] = starttime+dt.timedelta(
        seconds=dfRGA.iloc[i, 0])
    dfRGA.iloc[i, 0] = round_seconds(dfRGA.iloc[i, 0])
dfRGA = dfRGA.loc[:, ~dfRGA.columns.str.contains('^Unnamed')]
#dfRGA = dfRGA.loc[239:]

#%%Import pressure data (csv from tdms)
datfile = 'Pressure Data\pressure_20230508.csv'
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
# istart = 8662
#%%Import pressure data (mat)
datfile = 'Pressure Data/2023_06_08_Vacuum_Pressures.mat'
pressures = loadmat(datfile)
ptime = np.transpose(pressures['Vacuum_Pressures_time'])
ConvAp = np.transpose(pressures['AP_TANK_PRESSURE'])
dfp1 = pd.DataFrame(data=list(
    zip(ptime, ConvAp)), columns=['Time', 'Aprime tank convectron'])

#for multiple days
datfile = 'Pressure Data/2023_06_09_Vacuum_Pressures.mat'
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
datfile = 'Pressure Data/2023_06_08_IG_Pressures.mat'
pressures = loadmat(datfile)
ptime = np.transpose(pressures['IG_Pressures_time'])
IGAp = np.transpose(pressures['AP_IG_PRESSURE'])
dfIG1 = pd.DataFrame(data=list(
    zip(ptime, IGAp)), columns=['Time', 'Aprime ion gauge'])

#for multiple days
datfile = 'Pressure Data/2023_06_09_IG_Pressures.mat'
pressures = loadmat(datfile)
ptime = np.transpose(pressures['IG_Pressures_time'])
IGAp = np.transpose(pressures['AP_IG_PRESSURE'])
dfIG2 = pd.DataFrame(data=list(
    zip(ptime, IGAp)), columns=['Time', 'Aprime ion gauge'])
dfIG = pd.concat([dfIG1, dfIG2], ignore_index=True)

for k in range(len(dfIG["Time"])):
    dfIG.iloc[k, 0] = float(dfIG.iloc[k,0])
    dfIG.iloc[k, 0] = dt.datetime.utcfromtimestamp(
        dfIG.iloc[k, 0]).replace(tzinfo=dt.timezone.utc)
    dfIG.iloc[k, 0] = dfIG.iloc[k, 0].astimezone(
        pytz.timezone('Etc/GMT+5'))
    dfIG.iloc[k, 0] = dfIG.iloc[k, 0].replace(tzinfo=None)
IGdata = dfIG['Aprime ion gauge']

#%%Import current data
datfile = 'Current Data\GDC_Voltages_20230508.csv'
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

#%% Plotting    
#Generate figure and subplot
fig = plt.figure(figsize=(8,8))
ax1 = fig.add_subplot(611)
ax2 = fig.add_subplot(612, sharex=ax1)
ax3 = fig.add_subplot(613, sharex=ax1)
ax4 = fig.add_subplot(614, sharex=ax1)
ax5 = fig.add_subplot(615, sharex=ax1)
ax6 = fig.add_subplot(616, sharex=ax1)

#set the color_cylce to make colors different across subplots
color_cycle = plt.rcParams['axes.prop_cycle']()

#Plot the raw data for each mass number
for (columnName, columnData), cc in zip(dfRGA.items(), color_cycle):
    if columnName == "Time(s)":
        continue
    if columnName == workinggas:
        ax1.plot(dfRGA["Time(s)"], columnData, label=str(columnName),**cc)
    elif columnName in {"Hydrogen", "Helium"}:
        ax2.plot(dfRGA["Time(s)"], columnData, label=str(columnName),**cc)
    elif columnName in {"Oxygen", "Water", "Nitrogen"}: 
        ax3.plot(dfRGA["Time(s)"], columnData, label=str(columnName),**cc)
    elif columnName in {"Carbon dioxide", "Carbon", "Carbon Dioxide", "Argon"}:
        ax4.plot(dfRGA["Time(s)"], columnData, label=str(columnName),**cc)

#plot pressure data
# ax5.plot(dfp["Time"].iloc[istart:iend], pdata[istart:iend])

#plot IG data
ax5.plot(dfIG["Time"], IGdata)

# #Plot current data
# for (columnName, columnData) in dfc.items():
#     if columnName == "Time(s)":
#         continue
#     ax6.plot(dfc["Time(s)"], columnData, label=str(columnName))

#Set axis labels and legends
fmt = mdates.DateFormatter('%H:%M')

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

ax5.xaxis.set_major_formatter(fmt)
ax5.set_ylabel("Pressure(Torr)")
ax5.ticklabel_format(style='sci', scilimits=(0,0), axis='y')
ax5.set_title("IG Pressure")

# ax6.xaxis.set_major_formatter(fmt)
# ax6.set_xlabel("Time(s)")
# ax6.set_ylabel("Pressure(Torr)")
# ax6.set_title("IG Pressure")

# ax6.xaxis.set_major_formatter(fmt)
# ax6.set_xlabel("Time(s)")
# ax6.set_ylabel("Current(A)")
# ax6.set_title("Glow Current")
# ax6.legend(loc='center left', bbox_to_anchor=(1,0.5))

fig.tight_layout()
plt.show()







