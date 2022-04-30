'''
1. Get all the catalogue from Debonairs
'''
# prettier-ignore
from ast import Try
from cmath import pi
from tkinter import E
from unicodedata import category
from numpy import disp
from pymongo import MongoClient
import time
from random import randint
import sys
import os
sys.path.append('../')
from tqdm import tqdm
import csv
import re
from bs4 import BeautifulSoup
import requests
from colorama import Back, Fore, Style, init
init()
import datetime
from scrapingant_client import ScrapingAntClient
import http.client
import json

conn = http.client.HTTPSConnection("api.scrapingant.com")


driver = False
wait = False

client = False
db = False
_SHOP_NAME_ = 'DEBONAIRS'

def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)

display_log(Fore.GREEN, 'ROBOT NAME: DEBOBOT')
display_log(Fore.GREEN, _SHOP_NAME_)

# Create a ScrapingAntClient instance
headers = {
   'x-api-key': "9d1df42476e649968ddb8d58a18cb5c6",
   'content-type': "application/json",
   'accept': "application/json"
}

def getHTMLDocument(url):
    response = requests.get(url)
    return response.text


def launchBot():
    _INDEX_START_MENU_ITEM_ = 55553

    try:
        payload = "{ \"url\": \"https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall\"}"
        #1. Get the main page
        conn.request("POST", "/v1/general", payload, headers)

        res = conn.getresponse()
        data = res.read()

        soup = BeautifulSoup(json.loads(data.decode("utf-8"))['content'], 'html.parser')
        
        #List all the categories of pizzas
        pizzas_categories = soup.find_all('div', {'class':'m__listing'})

        for index, parent_set in enumerate(pizzas_categories):
            #Get the name of the category
            category = str(parent_set.find('div', {"class":'m__listing__category-title--text'}).find('h2').get_text()).replace("\"", "").strip()
            #Get the details of each pizzas
            pizzas_targeted_set = parent_set.find_all('div', {'class':'m-list-item'})
            
            display_log(Fore.YELLOW, '[{}] {}'.format(index+1, category))

            for j, pizza_type in enumerate(pizzas_targeted_set):
                #Get the pizza name for linking
                pizza_name = str(pizza_type.find('h3', {'class':'m-list-item__name'}).get_text()).replace("\"","").strip()
                #? Create the modal link
                item_number = _INDEX_START_MENU_ITEM_
                #https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/55553/garlic-bacon-%E2%80%98n-jalape%C3%B1o-(new)
                pizza_name_asURL = str(pizza_name).lower().strip().replace(' ','-')
                
                _INDEX_START_MENU_ITEM_ = 55572 if pizza_name_asURL is 'custard-malva-pudding-(new)' else _INDEX_START_MENU_ITEM_

                item_number = 55432 if pizza_name_asURL is 'on-the-double®' else 55570 if pizza_name_asURL is 'on-the-double®-feast' else 55433 if pizza_name_asURL is 'on-the-triple®' else 55571 if pizza_name_asURL is 'on-the-triple®-feast' else _INDEX_START_MENU_ITEM_

                #! Exlude: on the double/triple
                if pizza_name_asURL in ['on-the-double®', 'on-the-double®-feast', 'on-the-triple®', 'on-the-triple®-feast'] is False:
                    print('{} -> {}'.format(item_number, pizza_name_asURL))

                    payload = "{ \"url\": \"https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/"+ str(item_number) +"/"+ pizza_name_asURL +"\"}"
                    
                    #1. Get the main page
                    conn.request("POST", "/v1/general", payload.encode('utf-8'), headers)

                    res = conn.getresponse()
                    data = res.read()

                    if data.decode("utf-8") is not None:
                        soupPizza = BeautifulSoup(json.loads(data.decode("utf-8"))['content'], 'html.parser')

                        #? Extract the name, description, picture and options
                        name = soupPizza.find('div', {'class':'mi__description'}).find('h1').get_text()
                        description = soupPizza.find('div', {'class':'mi__description'}).find('p').get_text()
                        # get the options
                        options_set = soupPizza.find('div', {'class':'mi__option_parent'}).find('div', {'class':'mi__option'})
                        
                        #? Get the pizza size options
                        options_domain = options_set.find('div').find('ul').find_all('li')
                        pizza_size = [
                            {
                                'name': str(options_domain[0].find('label').get_text()).replace('+','').strip(),
                                'price': str(options_domain[0].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            },
                            {
                                'name': str(options_domain[1].find('label').get_text()).replace('+','').strip(),
                                'price': str(options_domain[1].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            },
                            {
                                'name': str(options_domain[2].find('label').get_text()).replace('+','').strip(),
                                'price': str(options_domain[2].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            },
                        ]

                        #? Get the base, cheese and extra toppings details
                        other_options_domain = options_domain[3].find('div', {'class':'mi__radio_parent'}).find('div').find_all('div', {'class':'mi__option'})

                        #1. Base
                        base_data = other_options_domain[0].find('div').find('ul').find_all('li')
                        pizza_base = [
                            {
                                'name': str(base_data[0].find('label').get_text()).replace('+','').strip(),
                                'price': str(base_data[0].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            },
                            {
                                'name': str(base_data[1].find('label').get_text()).replace('+','').strip(),
                                'price': str(base_data[1].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            },
                            {
                                'name': str(base_data[2].find('label').get_text()).replace('+','').strip(),
                                'price': str(base_data[2].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            },
                            {
                                'name': str(base_data[3].find('label').get_text()).replace('+','').strip(),
                                'price': str(base_data[3].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            }
                        ]
                        
                        #2. Cheese
                        cheese_data = other_options_domain[1].find('div').find('ul').find_all('li')
                        pizza_cheese = [
                            {
                                'name': str(cheese_data[0].find('label').get_text()).replace('+','').strip(),
                                'price': str(cheese_data[0].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            },
                            {
                                'name': str(cheese_data[1].find('label').get_text()).replace('+','').strip(),
                                'price': str(cheese_data[1].find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            }
                        ]

                        #3. Extra toppings and sauce
                        extra_toppings_data = other_options_domain[2].find('div').find('ul').find_all('li')

                        # print(extra_toppings_data)
                        pizza_toppings = []
                        for index, topping in enumerate(extra_toppings_data):
                            tmpData = {
                                'name': str(topping.find('label').get_text()).replace('+','').strip(),
                                'price': str(topping.find('span', {'class':'mi__option-price'}).get_text()).replace('+','').strip()
                            }
                            #...
                            pizza_toppings.append(tmpData)
                        
                        

                else:
                    display_log(Fore.RED, 'Some encoding is wrong.')
                    print(payload)

                #! Keep going with the item number - crucial
                _INDEX_START_MENU_ITEM_ += 1
                break
            break

    except Exception as e:
        print(e.with_traceback())


#!Debug
launchBot()