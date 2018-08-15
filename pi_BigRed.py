from twython import Twython
import bs4 as bs
import pickle
import requests
import datetime as dt
import os
import schedule
import fix_yahoo_finance as yf

import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
from pandas.compat import u
from pandas.tools.plotting import table

style.use('ggplot')
yf.pdr_override()

#twitter credentials (BigRedBiotech)

def twitter_setup():
    twittertxt = open('BigRedBiotech_twitter.txt')
    creds = {}
    for line in twittertxt:
        key, val = line.strip().split('\t')
        creds[key] = val

    APP_KEY = creds['API Key']
    APP_SECRET = creds['API Secret']
    OAUTH_TOKEN = creds['Access Token']
    OAUTH_TOKEN_SECRET = creds['Access Token Secret']

    twitter = Twython(APP_KEY, APP_SECRET,
                      OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

#Get the change in stock price
def ticker_returns(tick, day0, day1):
    temp_frame = web.get_data_yahoo(tick, day0, day1)
    day0_close = temp_frame.loc[day0.date()]['Close']
    day1_close = temp_frame.loc[day1.date()]['Close']
    percent_change = (day1_close-day0_close)/day0_close*100
    money_change = day1_close-day0_close
    vol = temp_frame.loc[day1.date()]['Volume']
    points = [day1_close, money_change, percent_change, int(vol)]
    
    return points

def golden_retreiver():
    tick_table = pd.read_excel('biotechs.xlsx') #Read in all the biotech tickers
    tickers = tick_table['Ticker'].tolist() #make an iterable list of the tickers
    today = dt.datetime.today()
    today =today.replace(day=today.day-1, hour=23) #adjust for being in Tokyo, and also be sure time is after close
    previous_day =today.replace(day=today.day-5) #getting a five day spread to cover most situations

    returns = {} #create a dictionary to store data retreived
    for tic in tickers:
        returns[tic] = ticker_returns(tic, yesterday, today) 
    
    #create a pandas dataframe from the dictionary
    df = pd.DataFrame.from_dict(returns, orient='index', 
                               columns=['Close', '\u0394$', '\u0394%','Volume'])
    sortdf = df.sort_values(by='\u0394%') #sort by %change, ascending, and save to new df
    decimals = pd.Series([2, 2, 3, 0], index=['Close', '\u0394$', '\u0394%','Volume']) #simplify display by rounding
    sorthead = sortdf.round(decimals).head(10) #Just take the top ten losers for the day

#create and save fig
def fig_creator(data_frame): #bring in sorthead as the data_frame
    fig, ax = plt.subplots(figsize=(12, 4)) # set size frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
    tabla = table(ax, data_frame, loc='upper left', colWidths=[0.12]*len(data_frame.columns))  # where df is your data frame
    tabla.auto_set_font_size(False) # Activate set fontsize manually
    tabla.set_fontsize(15) # if ++fontsize is necessary ++colWidths
    tabla.scale(1.5, 1.5) # change size table
    plt.savefig(f'{today.date()}_losers.png', transparent=True,bbox_inches='tight', dpi=300, pad_inches=0)


#tweet photo and tickers
def tweet():
    tweet_phrase = ', '.join(['$'+i for i in sorthead.index.tolist()])
    photo = open(f'{today.date()}_losers.png', 'rb')
    response = twitter.upload_media(media=photo)
    twitter.update_status(status=f'Big Red on {today.date()}:\n{tweet_phrase}', media_ids=[response['media_id']])
