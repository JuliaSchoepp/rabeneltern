#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 12:07:55 2020

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
    hours = str(int(x//60))
    minutes = str(int(x%60))
    time = hours + ":" + minutes
    if len(time) != 5:
        if time == "0:0":
            return "00:00"
        if time[1] == ":":
            return "0"+time
        elif time[-2] == ":":
            return time + "0"
    return time

#--Helper Function--
def create_df(file, colnames):
    """ 
    Takes in a file and the colnames and returns a df with rounded times
    """    
    df = pandas.read_csv(file, sep=';', names=colnames, header=None) #CSV einlesen
    df["Ereignis"] = df["Ereignis"].str.strip() # Leerzeichen entfernen
    df["Datum"] = df["Datum"].apply(convert_date)
    df["Zeit"] = df["Zeit"].apply(round_time).apply(convert_to_mins) # runden
    df["Nacht"] = [False if (480 < x < 1260) else True for x in df["Zeit"]]
    return df

#--Werte für Plot
def create_scatter_vals(df, event, y_val):  
    """ creates x,y and dotsize value from df. 
    Takes in the df, the list of events and a y-value (fixed int).
    """
    df_to = df.iloc[:, [1,2]].copy() # Dataframe mit Fokus auf Ereignis (ohne Datum)
    xs = list(df_to.loc[df_to["Ereignis"] == event]["Zeit"]) #get times filtered by event
    ys = [y_val for i in xs] # assigns position on y axis
    dotsizes = create_dotsize(xs) # creates dotsize according to frequency of the event
    return(xs, ys, dotsizes)

#--Variante 1: Alle Daten in einem Plot; X Ticks funtionieren
def plot_vals(df, colors, events):
    """
    plots.
    colors and events are lists
    """
    fig, ax = plt.subplots(figsize=(16,5))
    ax.axis([0, 1440, 0, 5])
    start, end = ax.get_xlim()
    formatter = FuncFormatter(my_ticks)
    plt.xticks(rotation=70)
    ax.xaxis.set_major_formatter(formatter)
    plt.yticks((1,2,3,4), events)
    ax.set_title("Jakobs Tag")
    for ind, ev in enumerate(events):
        (xs,ys,dotsizes) = create_scatter_vals(df, ev, (ind+1))
        plt.scatter(xs, ys, s=dotsizes, marker="o", alpha=0.5, color=colors[ind])
    plt.savefig("test1.pdf")
    return fig,ax

#--Variante 2: Subplot pro Zeitraum; funtioniert nur ohne die auskommentierten Zeilen;
# dann aber ohne formatierte x Ticks
def plot_subplots(df, colors, events, dates):
    """
    Input: equivalent to plt_vals + list of dates as tuple
    indicating start and end date as str of the format "%d.%m.%y".
    Creates a subplot for each period of observation as indicated
    by the start and end date in "dates".
    """
    size = 4*len(dates)
    fig, axs = plt.subplots(nrows=len(dates), ncols=1, figsize=(14,size))
    fig.suptitle("Jakobs Tag", fontsize="x-large", y=1.0)
    counter = 0
    for datepair in dates:
        ax = axs[counter]
        ax.axis([0, 1440, 0, 5])
        plt.sca(ax)
        plt.yticks((1,2,3,4), events)
        start, end = ax.get_xlim()
        #formatter = FuncFormatter(my_ticks)
        plt.xticks(rotation=70)
        #plt.xaxis.set_major_formatter(formatter)
        (start, end) = convert_date(datepair[0]), convert_date(datepair[1])
        df_filtered = df.loc[(start <= df["Datum"]) & (df["Datum"] <= end)]
        for ind, ev in enumerate(events):
            (xs,ys,dotsizes) = create_scatter_vals(df_filtered, ev, (ind+1))
            ax.scatter(xs, ys, s=dotsizes, marker="o", alpha=0.5, color=colors[ind])
        ax.title.set_text(str(datepair[0]) + " bis " + str(datepair[1]))
        counter += 1
    fig.tight_layout(pad=2.0)
    plt.savefig("test2.pdf")
    return fig,axs

def get_stats(df, event, night=False):
    """
    Input: df and event (str)
    Output: prints mean, max and min of event, returns df of event per day
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

def plot_stats(df, events_plot):
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

def plot_day_night(df, event):
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
    total_time = 0
    filtered = df.loc[(df["Ereignis"]=="Einschlafen") | (df["Ereignis"]=="Aufwachen")]
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
    
    
    

file = 'rabeneltern.csv'
colnames = ["Datum", "Zeit", "Ereignis"]
events = ["Stillen", "Brei", "Aufwachen", "Einschlafen"]
colors = ["#e0abce", "#f27844", "#b5f244", "#446af2"]

df = create_df(file, colnames)
dates = [("20.03.2020", "29.03.2020"), ("30.03.2020", "07.04.2020")]
#fig,ax = plot_vals(df, colors, events)
#fig, axs = plot_subplots(df, colors, events, dates)
#stats = get_stats(df, "Aufwachen")   
#stats2 = get_stats(df, "Stillen", night=True)     
events_plot = ["Stillen", "Aufwachen", "Einschlafen"]

#plot_stats(df, events_plot)
#plot_day_night(df, "Stillen")
