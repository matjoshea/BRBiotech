
# coding: utf-8

# In[59]:

from twython import Twython
import bs4 as bs
import pickle
import requests
import datetime as dt
import os
import imgkit
import fix_yahoo_finance as yf

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

#twitter credentials (bioteHK)
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


# In[3]:

def ticker_returns(tick, day0, day1):
    temp_frame = web.get_data_yahoo(tick, day0, day1)
    day0_close = temp_frame.iloc[-2]['Close']
    day1_close = temp_frame.iloc[-1]['Close']
    percent_change = (day1_close-day0_close)/day0_close*100
    money_change = day1_close-day0_close
    vol = temp_frame.loc[day1.date()]['Volume']
    points = [day1_close, money_change, percent_change, int(vol)]
    
    return points


# In[4]:

#Find the losers
tick_table = pd.read_excel('biotechs.xlsx')
tickers = tick_table['Ticker'].tolist()
today = dt.datetime.today()
today =today.replace(day=today.day-1, hour=23)
yesterday =today.replace(day=today.day-5)

returns = {}
for tic in tickers:
    returns[tic] = ticker_returns(tic, yesterday, today)


# In[5]:

df = pd.DataFrame.from_dict(returns, orient='index',
                           columns=['Close', '\u0394$', '\u0394%','Volume'])
sortdf = df.sort_values(by='\u0394%')
decimals = pd.Series([2, 2, 3, 0], index=['Close', '\u0394$', '\u0394%','Volume'])
sorthead = sortdf.round(decimals).head(10)

#html = sorthead.style.render()
#imgkit.from_string(html, 'table2.png')


# In[6]:

fig, ax = plt.subplots(figsize=(12, 4)) # set size frame
ax.xaxis.set_visible(False)  # hide the x axis
ax.yaxis.set_visible(False)  # hide the y axis
ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
tabla = table(ax, sorthead, loc='center', colWidths=[0.12]*len(sorthead.columns))  # where df is your data frame
tabla.auto_set_font_size(False) # Activate set fontsize manually
tabla.set_fontsize(15) # if ++fontsize is necessary ++colWidths
tabla.scale(1.5, 1.5) # change size table
plt.savefig(f'images/{today.date()}_losers.png', transparent=True,bbox_inches='tight', dpi=300, pad_inches=0)


# In[7]:

losing_tickers = sorthead.index.tolist()
tweet_phrase = ', '.join(['$'+i for i in losing_tickers])
photo = open(f'images/{today.date()}_losers.png', 'rb')
response = twitter.upload_media(media=photo)
twitter.update_status(status=f'Big Red on {today.date()}:\n{tweet_phrase}', media_ids=[response['media_id']])


# In[73]:

pandadf = sortdf.sort_values(by='\u0394%', ascending=False).round(decimals).head(10)
pandadf = pandadf.applymap(str)
fig, ax = plt.subplots(figsize=(10, 4)) # set size frame
ax.xaxis.set_visible(False)  # hide the x axis
ax.yaxis.set_visible(False)  # hide the y axis
#ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
tabla = table(ax, pandadf, loc='center', colWidths=[0.12]*len(pandadf.columns))  # where df is your data frame
tabla.auto_set_font_size(False) # Activate set fontsize manually
tabla.set_fontsize(15) # if ++fontsize is necessary ++colWidths
tabla.scale(1.5, 1.5) # change size table
panda_file = f'pandas/{today.date()}_pandas.png'
plt.savefig(panda_file, transparent=True,bbox_inches='tight', dpi=300, pad_inches=0)

bg = Image.open("panda.jpg")
bg2 = Image.open("panda.jpg")
fg = Image.open(panda_file)
imbg_width, imbg_height = bg.size
fg_resized = fg.resize((imbg_width, imbg_height), Image.LANCZOS)
bg.paste(fg_resized, None, fg_resized)
Image.blend(bg2, bg, .6).resize((int(imbg_width/2), int(imbg_height/2)), Image.ANTIALIAS).save(f"pandas/{today.date()}_panda_out.png")


# In[72]:

panda_tickers = pandadf.index.tolist()
tweet_phrase = ', '.join(['$'+i for i in panda_tickers])
photo = open(f'pandas/{today.date()}_panda_out.png', 'rb')
response = twitter.upload_media(media=photo)
twitter.update_status(status=f'Chinese Big Red on {today.date()}:\n{tweet_phrase}', media_ids=[response['media_id']])


# In[ ]:



