'''
1. Get all the catalogue from KFC
'''
# prettier-ignore
from ast import Try
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
_SHOP_NAME_ = 'KFC'
_CATEGORY_GENERAL = 'FOOD'

def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)

display_log(Fore.GREEN, 'ROBOT NAME: KFC-BOT')
display_log(Fore.GREEN, _SHOP_NAME_)

_DEALS_AUTHORISED = [
    'Buckets',
    'Family Treat',
    'Box Meals',
    'Burgers',
    'Twisters',
    'Streetwise',
    'Wings',
    'Anytime Snacking',
    'Snacks & Sides',
    'Drinks',
    'Treats'
]

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
    try:
        client = MongoClient(
                    'mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')

        db = client.NEJ
        collection_catalogue = db['catalogue_central']

        payload = "{ \"url\": \"https://order.kfc.co.za/menu/bucket\"}"
        print(payload)

        conn.request("POST", "/v1/general", payload, headers)

        res = conn.getresponse()
        data = res.read()

        soup = BeautifulSoup(json.loads(data.decode("utf-8"))['content'], 'html.parser')
        # #List all the vailable deals and iterate
        parent_data = soup.find_all('div', {"class":"menu-list ng-scope"})

        for j, product in enumerate(parent_data):
            #?1. Get the category name
            category = str(product.find('h2', {"class":"d-md-block ng-binding"}).get_text()).strip()
            
            if category in _DEALS_AUTHORISED:
                display_log(Fore.YELLOW, '[{}]. {}'.format(j+1, category))
                #! Go through the indiviual products
                meals_types = product.find_all('div', {"class":"ng-isolate-scope meal-type"}) if len(product.find_all('div', {"class":"ng-isolate-scope meal-type"}))>0 else product.find_all('div', {"class":"meal-type ng-isolate-scope"})

                for k, meal in enumerate(meals_types):
                    # Extract the picture, name, price and id?
                    meal_name = str(meal.find('div', {"class":"product-name-desc"}).find_all('div')[0].get_text()).strip()
                    meal_price = str(meal.find('div', {"class":"product-name-desc"}).find_all('div')[1].get_text()).strip()
                    meal_picture = 'https://order.kfc.co.za/' + str(meal.find('div', {"class":"product-item-img"}).find('img')['src']).strip()
                    #? SAVE in the db
                    #Compile the whole product data model
                    TMP_DATA_MODEL = {
                       'brand': _SHOP_NAME_,
                        'product_name': meal_name,
                        'product_price': meal_price,
                        'product_picture': meal_picture,
                        'sku': str(meal_name).upper(),
                        'used_link': 'https://order.kfc.co.za/menu/bucket',
                        'meta': {
                            'category': str(category).upper().strip(),
                            'subcategory': str(category).upper().strip(),
                            'shop_name': _SHOP_NAME_,
                            'website_link': 'https://order.kfc.co.za/'
                        },
                        'date_added':  datetime.datetime.today().replace(microsecond=0)
                    }

                    #! filter
                    filterProduct = {
                        'brand': _SHOP_NAME_,
                        'product_name': meal_name,
                        'meta.category': str(category).upper().strip(),
                        'meta.subcategory': str(category).upper().strip(),
                        'meta.shop_name': _SHOP_NAME_
                    }
                    
                    checkExistense = collection_catalogue.find(filterProduct)

                    if checkExistense.count() > 0: #Exists
                        #update
                        print(TMP_DATA_MODEL)
                        display_log(Fore.LIGHTBLUE_EX, 'Updating the product model in catalogue')
                        collection_catalogue.update_one(filterProduct, {"$set": {'product_price': TMP_DATA_MODEL['product_price']}})
                    else: #no records yet
                        print(TMP_DATA_MODEL)
                        display_log(Fore.GREEN, 'Saving the product model in catalogue')
                        collection_catalogue.update_one(filterProduct, {"$set": TMP_DATA_MODEL}, upsert=True)
                print('----------')
            else:
                display_log(Fore.RED, 'Unauthorised package [{}]'.format(category))
    
    except Exception as e:
        print(e)



#!Debug
launchBot()