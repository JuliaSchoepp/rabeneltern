#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 08:55:53 2020

@author: juliaschopp
"""
import pandas
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates


# --Helper Function--
def convert_date(date):
    """converts a time str of format "%d.%m.%Y" to datetime format"""
    return datetime.strptime(date, "%d.%m.%Y")

# --Hepler Function: Konvertiert die Zeit in Minuten, da 
# ich mit den datetime/matplotlib Zeitformaten gescheitert bin
def convert_to_mins(time):
    """ 
    Input: Time (str) in Format HH:MM
    Output: Number of mins (int)
    """
    assert len(time) == 5, "Incorrect format"
    hours = int(time[-5:-3])
    minutes = int(time[-2:])
    return (hours*60+minutes)

# --Helper Function-    
def create_dotsize(zeiten, factor=50):
    """takes in an list/array and returns 1 when the element occurs for
    the first time, 2 the second etc."""
    l = []
    counter = {}
    for i in zeiten:
        if i not in counter:
            l.append(1)
            counter[i] = 1
        else:
            counter[i] += 1
            l.append(counter[i])
    return (np.array(l))*factor

# -- Helper Function -- 
def round_time(zeit):
    """
    Input: Date str of format last 5 digits HH:MM
    Output: Date str rounded to full 10 minutes, up from :05 -> :10
    """
    time_gekürzt = zeit[:-2]
    last_1 = int(zeit[-1])
    last_2 = int(zeit[-2:])
    second_to_last = int(zeit[-2])
    hour = zeit[-5:-3]
    if last_1 == 0:
        return zeit
    elif 0 < last_1 < 5:
        l2 = zeit[-2] + str(0)
    else:
        if second_to_last == 5:
            fullhour = zeit[:-4] + str(int(zeit[-4])+1) + ":00"
            if fullhour[-5:] == "24:00":
                return zeit[:-5] + "00:00"
            elif hour == "09":
                return zeit[:-5] + "10:00"
            elif hour == "19":
                return zeit[:-5] + "20:00"
            else:  
                return fullhour
        else:
            l2 = (last_2 + 9) // 10 * 10
    return time_gekürzt + str(l2)

#-- Helper Function--
def my_ticks(x, pos):
    """ Helper func to convert day in minutes back to HH:MM strings for x ticks"""
    hours = int(x//60)
    if hours >= 10:
        hours = str(hours)
    else:
        hours = "0" + str(hours)
    minutes = int(x%60)
    if minutes >= 10:
        minutes = str(minutes)
    else:
        minutes = "0"+str(minutes)
    time = hours + ":" + minutes
    return time

#--Helper Function--
def create_df(file, colnames, timespan=(), rounded=False):
    """ 
    Input: 
    -csv file, 
    -list of column names
    -Rounded (bool), default False - True if the times should be rounded to full 10 mins
    -timespan, default empty, tuple of start end end date (str) to limit df
    Output:
     -pandas df, 
     -sorted by date and time
     -columns Nacht: True if time (Zeit) is between 08:00 and 21:00
    """    
    df = pandas.read_csv(file, sep=';', names=colnames, header=None) #CSV einlesen
    df.Ereignis = df.Ereignis.str.strip() # Leerzeichen entfernen
    df.Datum = df.Datum.apply(convert_date)
    if rounded == True:
        df.Zeit = df.Zeit.apply(round_time) # runden
    df.Zeit = df.Zeit.apply(convert_to_mins)
    df["Nacht"] = [False if (480 < x < 1260) else True for x in df.Zeit]
    df.sort_values(["Datum", "Zeit"])
    if len(timespan) == 2:
        (start, end) = convert_date(timespan[0]), convert_date(timespan[1])
        df = df.loc[(start <= df["Datum"]) & (df["Datum"] <= end)]
    return df