#!/usr/bin/env python
#
#  Copyright (c) 2007-2008, Corey Goldberg (corey@goldb.org)
#
#  license: GNU LGPL
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.

import urllib

"""
This is the "ystockquote" module.

This module provides a Python API for retrieving stock data from Yahoo Finance.

sample usage:
>>> import ystockquote
>>> print ystockquote.get_price('GOOG')
529.46
"""


def request(symbol, stat):
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
    return urllib.urlopen(url).read().strip().strip('"')

def get_all(symbol):
    """
    Get all available quote data for the given ticker symbol.
    
    Returns a dictionary.
    """
    values = request(symbol, 'l1c1va2xj1b4j4dyekjm3m4rr5p5p6s7pl1ohgd1t1n').split(',')
    data = {}
    data['price'] = values[0]
    data['change'] = values[1]
    data['volume'] = values[2]
    data['avg_daily_volume'] = values[3]
    data['stock_exchange'] = values[4]
    data['market_cap'] = values[5]
    data['book_value'] = values[6]
    data['ebitda'] = values[7]
    data['dividend_per_share'] = values[8]
    data['dividend_yield'] = values[9]
    data['earnings_per_share'] = values[10]
    data['52_week_high'] = values[11]
    data['52_week_low'] = values[12]
    data['50day_moving_avg'] = values[13]
    data['200day_moving_avg'] = values[14]
    data['price_earnings_ratio'] = values[15]
    data['price_earnings_growth_ratio'] = values[16]
    data['price_sales_ratio'] = values[17]
    data['price_book_ratio'] = values[18]
    data['short_ratio'] = values[19]

    # Added by StockBook developers.
    data['prev_close'] = values[20]
    data['last_trade'] = values[21]
    data['opening'] = values[22]
    data['high_day'] = values[23]
    data['low_day'] = values[24]
    data['day'] = values[25]
    data['time'] = values[26]
    data['code'] = symbol
    data['full_name'] = values[27][1:]

    return data
              
    
# =======  
# Direct requests from finance.yahoo
# Can also request information from our database:
# data = StockRetrieve.getIndexComponents('XXX')
# data['INFO'], where INFO can be: short_ratio, market_cap, or opening
# ======= 
def get_price(symbol): 
    return request(symbol, 'l1')


def get_change(symbol):
    return request(symbol, 'c1')
    
    
def get_volume(symbol): 
    return request(symbol, 'v')


def get_avg_daily_volume(symbol): 
    return request(symbol, 'a2')
    
    
def get_stock_exchange(symbol): 
    return request(symbol, 'x')
    
    
def get_market_cap(symbol):
    return request(symbol, 'j1')
   
   
def get_book_value(symbol):
    return request(symbol, 'b4')


def get_ebitda(symbol): 
    return request(symbol, 'j4')
    
    
def get_dividend_per_share(symbol):
    return request(symbol, 'd')


def get_dividend_yield(symbol): 
    return request(symbol, 'y')
    
    
def get_earnings_per_share(symbol): 
    return request(symbol, 'e')


def get_52_week_high(symbol): 
    return request(symbol, 'k')
    
    
def get_52_week_low(symbol): 
    return request(symbol, 'j')


def get_50day_moving_avg(symbol): 
    return request(symbol, 'm3')
    
    
def get_200day_moving_avg(symbol): 
    return request(symbol, 'm4')
    
    
def get_price_earnings_ratio(symbol): 
    return request(symbol, 'r')


def get_price_earnings_growth_ratio(symbol): 
    return request(symbol, 'r5')


def get_price_sales_ratio(symbol): 
    return request(symbol, 'p5')
    
    
def get_price_book_ratio(symbol): 
    return request(symbol, 'p6')
       
       
def get_short_ratio(symbol): 
    return request(symbol, 's7')
    
# First row:
# ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Clos']
# Others are actual data.
def get_historical_prices(symbol, start_date, end_date):
    """
    Get historical prices for the given ticker symbol.
    Date format is 'YYYYMMDD'
    
    Returns a nested list.
    """
    url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
          'd=%s&' % str(int(end_date[4:6]) - 1) + \
          'e=%s&' % str(int(end_date[6:8])) + \
          'f=%s&' % str(int(end_date[0:4])) + \
          'g=d&' + \
          'a=%s&' % str(int(start_date[4:6]) - 1) + \
          'b=%s&' % str(int(start_date[6:8])) + \
          'c=%s&' % str(int(start_date[0:4])) + \
          'ignore=.csv'
    days = urllib.urlopen(url).readlines()
    data = [day[:-2].split(',') for day in days]
    return data
