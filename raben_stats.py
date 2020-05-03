#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 09:10:50 2020

@author: juliaschopp
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates

from raben_helper import *

def get_stats(df, event, night=False):
    """
    Input: df and event (str), optional: night (bool), default False,
            to indicate whether data should be split for day & night
    Output: 
        if night=False:
            prints mean, max and min of event, returns count of event per day (df)
        if night=True:
            prints mean of event for day vs. night, returns tuple of 3 dfs:
            count of event at night, count of event at daytime, complete count
    """
    if not night:
        data = df.loc[df["Ereignis"] == event].groupby("Datum")
        count = data["Ereignis"].count()
        mean = count.mean()
        maxi = count.max()
        mini = count.min()
        print("Statistik für " + event + " : Im Schnitt " \
              + str(mean) + " mal, max: " + str(maxi) + " , min: " + str(mini))
        return count
    else:
        data_night = df.loc[(df["Ereignis"] == event) & (df["Nacht"] == True)].groupby("Datum")
        data_day = df.loc[(df["Ereignis"] == event) & (df["Nacht"] == False)].groupby("Datum")
        data_complete = get_stats(df, event, night=False)
        res = (data_night["Ereignis"].count(), data_day["Ereignis"].count(), data_complete)
        print(event + " nachts im Schnitt: " + str(res[0].mean()) + " , tags: "\
              + str(res[1].mean()))
        return res

def plot_stats(df, events_plot): # to do: add y-label, title, ...
    """
    Input: Df, list of events which should be plotted,
            night, a boolean which indicates whether night and day should be plotted
            seperately
    Output: A plot 
    """
    days = mdates.DayLocator()
    days_fmt = mdates.DateFormatter('%d.%m.')
    fig, ax = plt.subplots(figsize=(10,8))
    for e in events_plot:
        print(e)
        dates = [mdates.date2num(i) for i in get_stats(df,e).keys()]
        values = list(get_stats(df,e))
        ax.plot(dates, values, label=e)
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(days_fmt)
    fig.autofmt_xdate()
    plt.legend(loc='upper right')
    plt.show()

def plot_day_night(df, event): # to do: add y-label, title,...
    """
    Input:
        df, event(str)
    Output:
        plots number of event per day for day, night and total
    """
    days = mdates.DayLocator()
    days_fmt = mdates.DateFormatter('%d.%m.')
    fig, ax = plt.subplots(figsize=(10,8))
    data = get_stats(df, event, night=True)
    labels = ["Nachts", "Tags", "Gesamt"]
    count = 0
    for e in data:
        dates = [mdates.date2num(i) for i in e.keys()]
        values = list(e)
        ax.plot(dates, values, label=labels[count])
        count += 1
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(days_fmt)
    fig.autofmt_xdate()
    plt.legend(loc='upper right')
    plt.show()
 
def get_sleeping_stats(df):
    """
    Calculates the sleeping statistics for the whole timespan (as in df)
    __________
    Parameters
    ----------
    df (pandas df)
    Returns
    -------
    total_time : total sleeping time.
    time_per_day : total time divided by number of days
    """
    total_time = 0
    filtered = df.loc[(df.Ereignis == "Einschlafen") | (df.Ereignis=="Aufwachen")]
    inds = list(filtered.index)
    if df.iloc[inds[0],2] != "Einschlafen":
        inds.pop(0)
    if df.iloc[inds[-1],2] != "Aufwachen":
        inds.pop()
    timestamps = [df.iloc[ind,1] for ind in inds]
    while len(timestamps) != 0:
        sleeptime = timestamps.pop(0)
        waketime = timestamps.pop(0)
        total_time += abs(waketime - sleeptime)
    time_per_day = total_time/len(df.groupby("Datum"))
    print("Gesamt: " + str(total_time//60) + " Stunden " + str(total_time % 60) \
          + " Minuten verteilt auf " + str(len(df.groupby("Datum"))) + " Tage, also " \
              + str(int(time_per_day//60)) + " Stunden " + str(int(time_per_day%60)) + " Minuten" \
                  + " pro Tag.")
    return total_time, time_per_day


#--- Variables & Go

file = 'rabeneltern.csv'
colnames = ["Datum", "Zeit", "Ereignis"]
events = ["Stillen", "Brei", "Aufwachen", "Einschlafen"]
dates = [("20.03.2020", "29.03.2020"), ("30.03.2020", "07.04.2020"), \
("19.04.2020", "28.04.2020")]
    
events_plot = ["Stillen", "Aufwachen", "Einschlafen"] # for plot_stats

df = create_df(file, colnames, rounded=False, timespan=dates[2])

stats = get_stats(df, "Aufwachen")   
stats2 = get_stats(df, "Stillen", night=True)     

#plot_stats(df, events_plot)
#plot_day_night(df, "Stillen")

