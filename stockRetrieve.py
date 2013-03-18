import urllib
import csv
import ystockquote as ys           
from BeautifulSoup import BeautifulSoup, Tag                                           
import re
import json
from time import time

# SNIPCODE: Read a page from url.
# urllib.urlopen(url).read().strip().strip('"')

at = '%40'
continents = ['europe', 'americas', 'asia', 'africa']
#americanIndices = ['dow_jones', 'new_york', 'nasdaq', 'sp', 'other', 'treasury', 'commodities', 'futures']
americanIndices = ['nasdaq']
ukAndIrelandIndices = ['london']
italianIndices = ['milano', 'settoriali']

def _getIndices(listIndices, url, continent):
    pageContent = urllib.urlopen(url).read().strip().strip('"')
    soup = BeautifulSoup(pageContent)

    shortCodes = soup.findAll(attrs={'class': 'first'})
    del(shortCodes[0]) # first link is the header of the table
    
    fullNames = soup.findAll(attrs={'class': 'second name'})
    cont = []
    for i in range(0, len(shortCodes)):
        indexShortCode = shortCodes[i].findAll(text=True)
        indexShortCode = unicode.join(u'\n',map(unicode,indexShortCode))

        extendedIndexName = fullNames[i].findAll(text=True)
        extendedIndexName = unicode.join(u'\n',map(unicode,extendedIndexName))
        cont.append([indexShortCode, extendedIndexName])

    print continent
    listIndices[continent] = cont

# World + americans + british + italians = 15
def getAllIndices():
    print "Getting indices\n"
    listIndices = {}
    # for continent in continents:
    #     url = 'http://finance.yahoo.com/intlindices?e=%s' % continent
    #     _getIndices(listIndices, url, continent)

    # for americanIndex in americanIndices:
    #     url = 'http://finance.yahoo.com/indices?e=%s' % americanIndex
    #     _getIndices(listIndices, url, americanIndex)

    for british in ukAndIrelandIndices:
        url = 'http://uk.finance.yahoo.com/indices?e=%s' % british
        _getIndices(listIndices, url, british)

    # for italian in italianIndices:
    #     url = 'http://it.finance.yahoo.com/indices?e=%s' % italian
    #     _getIndices(listIndices, url, italian)
    
    return listIndices

# TODO - This is changing from list to dict
def getListComponents(symbol):
    components = {}
    page = 0
    while 1: 
        no_page = str(page) # start from 0, this is just for testing
        
        url = 'http://finance.yahoo.com/q/cp?s=%s&c=%s' % (symbol, no_page)
        pageContent = urllib.urlopen(url).read().strip().strip('"')
        soup = BeautifulSoup(pageContent)
        # id element in table is always the same
        links = soup.findAll(attrs={'class': 'yfnc_tabledata1'})
        if len(links) == 0:
            break

        i = 0
        limit = len(links)
        while i < limit:
            code = links[i].findAll(text=True)
            code = unicode.join(u'\n',map(unicode,code))
            fullName = links[i + 1].findAll(text=True)
            fullName = unicode.join(u'\n',map(unicode,fullName))
            # fifty_mov_avg = ys.get_50day_moving_avg(code)
            #wohund_mov_avg = ys.get_200day_moving_avg(code)
            pair = [code, fullName]#, fifty_mov_avg]#, twohund_mov_avg]
            components[code] = pair
            i = i + 5
        page += 1

    return components 

# World + americans + british + italians = 7309
# It takes around 7 minutes to run.
def getAllComponents():
    t = time()
    components = {}
    indicesPerContinent = getAllIndices()
    for continent in indicesPerContinent.keys(): # iterate over continents
        print continent + "start \n"
        indices = indicesPerContinent[continent]
        for index in indices: # iterate over indices
            indexComponents = getListComponents(index[0])
            for key in indexComponents.keys(): # iterate over components
                # key-code
                # indexComponents[key][1] - fullname
                # indexComponents[key][2] - 50mov avg
                # indexComponents[key][3] - 200mov avg
                print key
                data = [indexComponents[key][1]]#,#, indexComponents[key][3]]
                components[key] = data
        print continent + "end \n"
       

    t = time() - t
    print 'time ', t
    return components

# Useful: 
# http://resources.mdbitz.com/2010/02/understanding-yahoo-finance-stock-quotes-and-sl1d1t1c1ohgv/
def getAllComponentsInformation(symbol):
    return ys.get_all(symbol)

def getRealTimeData(symbol):
    values = ys.request(symbol, 'l1pohgd1t1').split(',')
    data = {}
    data['price'] = values[0] 

    # Added by StockBook developers.
    data['prev_close'] = values[1]
    data['opening'] = values[2]
    data['high_day'] = values[3]
    data['low_day'] = values[4]
    data['day'] = values[5]
    data['time'] = values[6]
    data['code'] = symbol
    return data

# Works with indices and components
def getHeadlines(symbol):
    headlinesList = []

    url = 'http://finance.yahoo.com/q/h?s=%s+Headlines' % symbol
    pageContent = urllib.urlopen(url).read().strip().strip('"')
    soup = BeautifulSoup(pageContent)
    
    tableHeadlines = soup.findAll(attrs={'class': 'mod yfi_quote_headline withsky'})
    #return headlines
    headlines = tableHeadlines[0].findAll(text=True)
    hrefs = tableHeadlines[0].findAll(href=True)

    # Remove headers
    del(headlines[0])
    del(hrefs[0])

    index = 0
    indexHeadlines = 0
    while 1:
        if (headlines[index] == ' '): # New day
            index += 2
        elif (headlines[index] == 'Older Headlines'): # No headlines anymore
            break

        headline = []
        headline.append(headlines[index])
        headline.append(headlines[index + 1])
        headline.append(headlines[index + 2])
        headline.append(hrefs[indexHeadlines]['href'])
        headlinesList.append(headline)

        indexHeadlines += 1

        index += 3

    headlinesSymbols = {}
    headlinesSymbols[symbol] = headlinesList
    return headlinesSymbols

def getMajorCurrencies():
    currencies = {}

    url = 'http://finance.yahoo.com/currency-investing/majors'
    pageContent = urllib.urlopen(url).read().strip().strip('"')
    soup = BeautifulSoup(pageContent)
        
    # =======
    # col1 - currency pair
    # col2 - price
    # col3 - change
    # col4 - change%
    # col5 - day range
    # col6 - 52 week range
    # =======
    firstPair = 1
    lastPair = 8
    currencyPairs = soup.findAll(attrs={'class':'col1'})[firstPair:lastPair + 1]  
    price = soup.findAll(attrs={'class':'col2'})[firstPair:lastPair + 1] 
    change = soup.findAll(attrs={'class':'col3'})[firstPair:lastPair + 1]  
    change_perc = soup.findAll(attrs={'class':'col4'})[firstPair:lastPair + 1]
    day_range = soup.findAll(attrs={'class':'col5'})[firstPair:lastPair + 1] 
    year_range = soup.findAll(attrs={'class':'col6'})[firstPair:lastPair + 1] 

    for i in range(0, len(currencyPairs)):
        data = []
        attribute = price[i].findAll(text=True)
        attribute = unicode.join(u'\n',map(unicode,attribute))
        data.append(attribute)

        attribute = change[i].findAll(text=True)
        attribute = unicode.join(u'\n',map(unicode,attribute))
        data.append(attribute)

        attribute = change_perc[i].findAll(text=True)
        attribute = unicode.join(u'\n',map(unicode,attribute))
        data.append(attribute)

        attribute = day_range[i].findAll(text=True)
        attribute = unicode.join(u'\n',map(unicode,attribute))
        data.append(attribute)
       
        attribute = year_range[i].findAll(text=True)
        attribute = unicode.join(u'\n',map(unicode,attribute))
        data.append(attribute)

        pair = currencyPairs[i].findAll(text=True)
        pair = unicode.join(u'\n',map(unicode,pair))
        currencies[pair] = data
    
    return currencies

# NOTE - This is for further uses.
# TODO - Maybe we could achieve this just playing with the variables: 
# http://resources.mdbitz.com/2010/02/understanding-yahoo-finance-stock-quotes-and-sl1d1t1c1ohgv/
def getComponentStatistics(symbol):
    componentStatistics = {}
    url = 'http://finance.yahoo.com/q/ks?s=%s+Key+Statistics' % symbol
    pageContent = urllib.urlopen(url).read().strip().strip('"')
    soup = BeautifulSoup(pageContent)

    # Tables
    # 0 - valuation measures
    # 1 - fiscal year
    # 2 - profitability
    # 3 - management effectiveness
    # 4 - income statement
    # 5 - balance sheet
    # 6 - cash flow statement
    # 7 - stock price history
    # 8 - share statistics
    # 9 - share statistics
    tables = soup.findAll(attrs={'class': 'yfnc_datamodoutline1'})
    

    for table in range(0, len(tables)):
        headings = tables[table].findAll(attrs={'class':'yfnc_tablehead1'})
        allTablesInformation = tables[table].findAll(text=True)
        
        index = 0
        indexHeadings = 0
        while index < len(allTablesInformation):
            fullHeadings = headings[indexHeadings].findAll(text=True)

            # Skip subtable title.
            if (fullHeadings[0] != allTablesInformation[index]):
                index = index + 1
            heading = headings[indexHeadings].findAll(text=True)[0] # only first one is meaningful text
            heading = unicode(heading)
            for fullHeading in range(0, len(fullHeadings)):
                if (allTablesInformation[index] == fullHeadings[fullHeading]):
                    index = index + 1

            componentStatistics[heading] = allTablesInformation[index]
            index = index + 1
            indexHeadings = indexHeadings + 1
    return componentStatistics

def getIndex(symbol):
    """
    Get all available quote data for the given ticker symbol.
    
    Returns a dictionary.
    """
    values = ys.request(symbol, 'l1c1xpohgd1t1n').split(',')
    data = {}
    data['price'] = values[0] 
    data['change'] = values[1]
    data['stock_exchange'] = values[2]

    # Added by StockBook developers.
    data['prev_close'] = values[3]
    data['opening'] = values[4]
    data['high_day'] = values[5]
    data['low_day'] = values[6]
    data['day'] = values[7]
    data['time'] = values[8]
    data['code'] = symbol
    data['full_name'] = values[9][1:] # TODO - Check

    return data

# =============
# JSON Methods
# =============
def getIndexJSON(symbol):
    return json.dumps(getIndex(symbol))

def getMajorCurrenciesJSON():
    return json.dumps(getMajorCurrencies())

def getHeadlinesJSON(symbol):
    return json.dumps(getHeadlines(symbol))

def getAllComponentsInformationJSON(symbol):
    return json.dumps(getAllComponentsInformation(symbol))

def getListComponentsJSON(symbol):
    return json.dumps(getListComponents(symbol))

def getListIndicesJSON():
    return json.dumps(getListIndices())

def get_historical_pricesJSON(symbol, start_date, end_date):
    return json.dumps(ys.get_historical_prices(symbol, start_date, end_date))
