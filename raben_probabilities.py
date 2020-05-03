#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 09:12:50 2020

@author: juliaschopp
"""
import pandas
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates

from raben_helper import *

def sleeping_probability(df, time):
    results = []
    time = convert_to_mins(time)
    days = df.Datum.unique() # get all the days
    data = df.loc[(df.Ereignis == "Einschlafen") | (df.Ereignis=="Aufwachen")].copy() #filter for sleeping and waking
    data.drop("Nacht", axis="columns", inplace=True) #drop unnecessary column
    # check sleeping status for each day
    for day in days: # to do: put in docstr that must be full days! (change in df)
        daily = data.loc[data.Datum == day]
        status = daily.loc[daily.Zeit == time].Ereignis
        if len(status) == 0: # if no exact match:
            try:
                ind = daily.loc[daily.Zeit < time].Zeit.idxmax() 
                # get index of closest value smaller than given time
                status = daily.loc[ind].Ereignis
            except ValueError: # if there is no smaller value for this day
                ind = daily.loc[daily.Zeit > time].Zeit.idxmin() #get next bigger value
                if daily.loc[ind].Ereignis == "Einschlafen": # set status as opposite of that value
                    status = "Aufwachen"
                else:
                    status = "Einschlafen"
        if type(status) != str:
            results.append(status.iloc[0])
        else:
            results.append(status)
    results = np.array([1 if x == "Einschlafen" else 0 for x in results])
    mean = results.mean()
    std = results.std()
    civ = 1.96*(((mean*(1-mean))/len(results)**0.5))
    return (mean, std, civ)

def plot_sleeping_p(df):
    times = [my_ticks(x, 0) for x in range(1440)]
    means = []
    civs = []
    for time in times:
        (mean, std, civ) = sleeping_probability(df, time)
        means.append(mean)
        civs.append(civ)
    upper_bounds = np.array(means) + np.array(civs)
    lower_bounds = np.array(means) - np.array(civs)
    fig, ax = plt.subplots(figsize=(24,10))
    ax.plot(range(1440), means, label="Wahrscheinlichkeit, dass Jakob schläft")
    #ax.plot(range(1440), upper_bounds, label="max. Wahrscheinlichkeit (95% Level)")
    #ax.plot(range(1440), lower_bounds, label="min. Wahrscheinlichkeit (95% Level)")
    ax.set_ylim(0, 1)
    ax.set_xlim(0,1440)
    formatter = FuncFormatter(my_ticks)
    plt.xticks(rotation=70)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(60.00))
    #ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))
    #ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.legend(loc='lower left')


#--- Variables & Go    
    
file = 'rabeneltern.csv'
colnames = ["Datum", "Zeit", "Ereignis"]

df = create_df(file, colnames, timespan=("20.03.2020", "02.05.2020"))
#dates = [("20.03.2020", "29.03.2020"), ("30.03.2020", "07.04.2020"), \
#("19.04.2020", "28.04.2020")]

