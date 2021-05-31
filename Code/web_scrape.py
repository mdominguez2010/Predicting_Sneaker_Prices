from bs4 import BeautifulSoup
import requests
import time, os
import re
import pickle

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent

import pandas as pd
import datetime
import numpy as np
import random

# Generate a list of shoe names


def shoes_list(n_pages):
    """
    Takes a number, which represents the number of pages to iterate through the StockX website, and returns a list of shoe names,
    which will be used later on
    """

    page_list = list(range(1,n_pages))
    shoes_list=[]

    for page in page_list:
        
        # Get URL into a BeautifulSoup object
        user_agent = {'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36'}
        url = 'https://stockx.com/retro-jordans?size_types=women&page={}'.format(page)
        response  = requests.get(url, headers = user_agent)
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        
        # Generate list
        current_shoes_list=[]
        for link in soup.find_all('a'):
            current_shoes_list.append(link.get('href'))
        
        # Focus on the shoe names
        shoes_list.extend(current_shoes_list[26:64])
        
        # Pause
        time.sleep(3+2*random.random())
    
    return shoes_list

def get_data(shoes_list):
    """
    Takes in the previously-created shoes_list and crawls on StockX to retreive the data
    """

    x_paths=[1] 
    v_list=[]
    high_low=[]
    trade_range=[]
    size_list=[]
    price_list=[]
    sale_date_list=[]
    n_sales=[]
    price_premium=[]
    avg_price=[]

    for shoe in range(len(shoes_list)):
        
        shoe_type = shoes_list[shoe]
        
        # Get URL into a BeautifulSoup object
        user_agent = {'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36'}
        url = 'https://stockx.com' + shoe_type
        response  = requests.get(url, headers = user_agent)
        page = response.text
        soup = BeautifulSoup(page, "lxml")
        
        # Find 52-week high low data and put it in a list
        try:
            high_low = soup.find_all(class_='value-container')[0].text
        except:
            high_low = np.nan
        time.sleep(2+2*random.random())
        
        # Find trade range and put it in a liast
        try:
            trade_range = soup.find_all(class_='ds-range value-container')[0].text
        except:
            trade_range = np.nan
        time.sleep(2+1*random.random())
        
        # Find volatility and put in list
        volatility = soup.find_all(class_='value')[-1].text
        try:
            v_list = volatility
        except:
            v_list = np.nan
        
        # Find 12-month rolling data and put it in separate lists
        twelve = soup.find_all(class_='gauge-value')
        current_twelve = [twelve.text for twelve in twelve]
        try:
            n_sales = current_twelve[0]
        except:
            n_sales = np.nan
        try:
            price_premium = current_twelve[1]
        except:
            price_premium = np.nan
        try:        
            avg_price = current_twelve[2]
        except:
            avg_price = np.nan
            
        time.sleep(2+3*random.random())
        
        # Make list for sizes
        size_list = soup.find('span', class_='bid-ask-sizes').text

        # Make list for sale price
        price_list = soup.find('div', class_='sale-value').text

        # Make list for sale prices
        sale_date_list = np.nan
        
        # Create list of names of the current shoe name so it can be added to df
        name_list = [shoe_type for i in range(len(x_paths))]

        # Find retail price
        try:
            retail = soup.find(text='Retail Price').findNext().text
        except:
            retail = np.nan
        # Remove white space
        try:
            retail = "".join(retail.split())
        except:
            retail = np.nan
        # Make List
        retail_list = [retail for i in range(len(x_paths))]

        # Find release date
        try:
            release = soup.find(text='Release Date').findNext().text
        except:
            release = np.nan
        # Remove white space
        try:
            release = "".join(release.split())
        except:
            release = np.nan
        try:    
            release_list = [release for i in range(len(x_paths))]
        except:
            release_list = np.nan

        # Dataframe
        d = {'Name': name_list, 'Release Date': release_list, 'Retail Price': retail_list, 'Sale Price': price_list, 'Size': size_list, 'Sale Date': sale_date_list,
            '52wk High|Low': high_low, '12mo Trade Range': trade_range, 'Volatility': v_list, '# of Sales': n_sales,
            'Price Premium': price_premium, 'Avg Resale Price': avg_price}
        df_current = pd.DataFrame(data=d)
        df = pd.concat([df, df_current], ignore_index=True) # READ CSV INTO JUPYTER NOTEBOOK BEFORE RUNNING THIS LOOP
        
        # pause
        time.sleep(10+2*random.random())

    return df
