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
import matplotlib.ticker as ticker

from raben_helper import *

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
    #to do: take df.Datum.loc[0] und df.Datum.loc[-1], datetime.strftime() back to str, set as start&end
    fig, ax = plt.subplots(figsize=(16,5))
    ax.axis([0, 1440, 0, 5])
    start, end = ax.get_xlim()
    formatter = FuncFormatter(my_ticks)
    plt.xticks(rotation=70)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(60.00))
    ax.xaxis.set_major_formatter(formatter)
    plt.yticks((1,2,3,4), events)
    ax.set_title("Jakobs Tag") # to do: add dates (siehe oben)
    for ind, ev in enumerate(events):
        (xs,ys,dotsizes) = create_scatter_vals(df, ev, (ind+1))
        plt.scatter(xs, ys, s=dotsizes, marker="o", alpha=0.5, color=colors[ind])
    plt.savefig("test1.pdf")
    return fig,ax

#--Variante 2: Subplot pro Zeitraum
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
        formatter = FuncFormatter(my_ticks)
        plt.xticks(rotation=70)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(60.00))
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

#--- Variables & Go

file = 'rabeneltern.csv'
colnames = ["Datum", "Zeit", "Ereignis"]
events = ["Stillen", "Brei", "Aufwachen", "Einschlafen"]
colors = ["#e0abce", "#f27844", "#b5f244", "#446af2"]

df = create_df(file, colnames, rounded=True)
dates = [("20.03.2020", "29.03.2020"), ("30.03.2020", "07.04.2020"), \
("19.04.2020", "28.04.2020")]
#fig,ax = plot_vals(df, colors, events)
fig, axs = plot_subplots(df, colors, events, dates)

