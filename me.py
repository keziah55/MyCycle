#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 21:20:51 2018

@author: keziah
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime


def minsec_to_sec(s):
    
    s_spl = s.split(':')
    s_spl = list(map(int, s_spl))
    
    try:
        mns, sec = s_spl
    except ValueError:
        mns = s_spl[0]
        
    total = 60 * mns + sec
    
    return total


def normalise(time, value):
    """ Normalise a value wrt time
    
        Parameters
        ----------
        time : int
            time in seconds
        value : int/float
            value to be normalised
    """
    
    # minutes
    time /= 60
    
    return value / time
    

df = pd.read_csv('me.csv')

dflen = len(df)

#xname, *ynames = df.columns

df['Time_sec'] = np.array(list(minsec_to_sec(time) for time in df['Time']))

dist_norm = np.array(list(normalise(df.iloc[n]['Time_sec'], 
                                    df.iloc[n]['Distance (km)']) 
                     for n in range(dflen)))
    
cal_norm = np.array(list(normalise(df.iloc[n]['Time_sec'], 
                                   df.iloc[n]['Calories']) 
                    for n in range(dflen)))
    
dates = list(datetime.strptime(date, '%Y-%m-%d').date() for date in df['Date'])

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1_col = 'green'
ax2_col = 'lightskyblue'
ax2_col_dark = 'dodgerblue'



# ax1 y data
ax1.plot_date(dates, dist_norm, color=ax1_col, marker='x')
ax1.set_ylabel('Distance per minute (km/min)', color=ax1_col)
ax1.tick_params('y', color=ax1_col)

# ax2 y data
ax2.plot_date(dates, df['Odometer (km)'], color=ax2_col, marker='') 
ax2.fill_between(dates, 0, df['Odometer (km)'], facecolor=ax2_col)
ax2.set_ylabel('Total distance (km)', color=ax2_col_dark)
ax2.tick_params('y', colors=ax2_col_dark)

# put ax1 in front of ax2
ax1.set_zorder(ax2.get_zorder()+1)
ax1.patch.set_visible(False) # hide the 'canvas' 

# x axis settings
ax1.set_xlabel('Date')
ax1.tick_params('x', labelrotation=70)

fig.tight_layout()

plt.show()
plt.close()