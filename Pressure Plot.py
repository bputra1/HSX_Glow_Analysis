# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 12:47:02 2023

@author: Asus
"""

from scipy.io import loadmat
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import pytz

annots = loadmat(
    'Pressure Data\pressure_20230517.mat')
time = np.transpose(annots['Vacuum_Pressures_time'])
pressures = np.transpose(annots['AP_TANK_PRESSURE'])
newData = list(zip(time, pressures))
dfp = pd.DataFrame(data=newData, columns=['Time', 'Aprime tank convectron'])
for i in range(len(dfp["Time"])):
    dfp.iloc[i, 0] = float(dfp.iloc[i,0])
    dfp.iloc[i, 0] = dt.datetime.utcfromtimestamp(
        dfp.iloc[i, 0]).replace(tzinfo=dt.timezone.utc)
    dfp.iloc[i, 0] = dfp.iloc[i, 0].astimezone(
        pytz.timezone('Etc/GMT+5'))
    dfp.iloc[i, 0] = dfp.iloc[i, 0].replace(tzinfo=None)
#%%
plt.plot(dfp['Time(s)'], dfp['Aprime tank convectron'])
