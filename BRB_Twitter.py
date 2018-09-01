
# coding: utf-8

from twython import Twython
import bs4 as bs
import pickle
import requests
import datetime as dt
import os
import fix_yahoo_finance as yf
from pytz import timezone 

from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
from pandas.compat import u
from pandas.plotting import table

style.use('ggplot')
yf.pdr_override()

#twitter credentials (@BigRedBiotech)

def start_twitter():
    
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

def days():
    NY_today = dt.datetime.now(timezone('US/Eastern'))
    NY_minus5 = NY_today-dt.timedelta(5)
    return NY_today, NY_minus5

def ticker_returns(tick, day0, day1):
    temp_frame = web.get_data_yahoo(tick, day0, day1)
    day0_close = temp_frame.iloc[-2]['Close']
    day1_close = temp_frame.iloc[-1]['Close']
    percent_change = (day1_close-day0_close)/day0_close*100
    money_change = day1_close-day0_close
    vol = temp_frame.loc[day1.date()]['Volume']
    points = [day1_close, money_change, percent_change, int(vol)]
    
    return points

def da_tickers(spreadsheet):
    tick_table = pd.read_csv(spreadsheet)

    return tick_table['Ticker'].tolist()


def performance_dictionary(bear_list, start, end):
    returns = {}
    for tic in bear_list:
        returns[tic] = ticker_returns(tic, start, end)

    return returns
    
def sorted_frame(bear_dict, losers=True):
    df = pd.DataFrame.from_dict(bear_dict, orient='index',
                           columns=['Close', '\u0394$', '\u0394%','Volume'])
    sortdf = df.sort_values(by='\u0394%', ascending=losers)

    return sortdf

def round_head(bear_df, top=10):
    decimals = pd.Series([2, 2, 3, 0], index=['Close', '\u0394$', '\u0394%','Volume'])

    return bear_df.round(decimals).head(top)

def table_image(dframe, file_out):
    dframe = dframe.applymap(str)
    fig, ax = plt.subplots(figsize=(10, 4)) # set size frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
    tabla = table(ax, dframe, loc='center', colWidths=[0.12]*len(dframe.columns))  # where df is your data frame
    tabla.auto_set_font_size(False) # Activate set fontsize manually
    tabla.set_fontsize(15) # if ++fontsize is necessary ++colWidths
    tabla.scale(1.5, 1.5) # change size table
    plt.savefig(file_out, transparent=True,bbox_inches='tight', dpi=300, pad_inches=0)

def add_background(background_image, front_image, output):
    bg = Image.open(background_image)
    bg2 = Image.open(background_image)
    fg = Image.open(front_image)
    imbg_width, imbg_height = bg.size
    fg_resized = fg.resize((imbg_width, imbg_height), Image.LANCZOS)
    bg.paste(fg_resized, None, fg_resized)
    Image.blend(bg2, bg, .6).resize((int(imbg_width/2), int(imbg_height/2)), Image.ANTIALIAS).save(output)


def tweet_image(dframe, file_path, today, losers=True):
    df = dframe.index.tolist()
    photo = open(file_path, 'rb')
    response = twitter.upload_media(media=photo)
    if losers:
        tweet_phrase = 'Big Red on {today.date()}:\n'+', '.join(['$'+i for i in df])
        twitter.update_status(status=tweet_phrase, media_ids=[response['media_id']])
    else:
        tweet_phrase = 'Chinese Big Red on {today.date()}:\nBig Red on {today.date()}:\n'+', '.join(['$'+i for i in df])
        twitter.update_status(status=tweet_phrase, media_ids=[response['media_id']])
        

def update_BRB(tweet=False):
    end, start = days()
    tickers = da_tickers('biotechs.csv')
    perf_dict = performance_dictionary(tickers, start, end)
    bear_frame = sorted_frame(perf_dict)
    panda_frame = sorted_frame(perf_dict, losers=False)
    bear_10 = round_head()
    panda_10 = round_head()
    bear_out = 'images/{}_losers2.png', end.date()
    panda_out = 'pandas/{}_pandas2.png', end.date()
    table_image(bear_10, bear_out)
    table_image(panda_10, panda_out)
    add_background('panda.jpg', panda_out, panda_out)

    if tweet:
        start_twitter()
        tweet_image(bear_10, bear_out, end)
        tweet_image(panda_10, panda_out, end, losers=False,)

update_BRB()
        




