'''
1. Get all the catalogue from Checkers.
'''
# prettier-ignore
from ast import Try
from logging import root
from math import ceil
from tkinter import E
from unicodedata import category
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
import urllib.parse
from scrapingant_client import ScrapingAntClient
import http.client
import json

conn = http.client.HTTPSConnection("api.scrapingant.com")


driver = False
wait = False

client = False
db = False
_SHOP_NAME_ = 'CHECKERS'

def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)

display_log(Fore.GREEN, 'ROBOT NAME: CHECK-BOT')
display_log(Fore.GREEN, _SHOP_NAME_)

# Create a ScrapingAntClient instance
headers = {
   'x-api-key': "5ac50d549a1a43f2b4a9bda94d353b56",
   'content-type': "application/json",
   'accept': "application/json"
}


def getHTMLSOUPEDDocument(url):
    payload = "{ \"url\": \""+ url +"\"}"
    #1. Get the main page
    conn.request("POST", "/v1/general", payload, headers)

    res = conn.getresponse()
    data = res.read()

    soup = BeautifulSoup(json.loads(data.decode("utf-8"))['content'], 'html.parser')
    return soup


def launchBot():
    try:
        client = MongoClient(
                    'mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')

        db = client.NEJ
        collection_catalogue = db['catalogue_central']

        root_url = 'https://www.checkers.co.za'

        #1. Get the main categories
        categories_page = getHTMLSOUPEDDocument(root_url)
        #List all the categories
        main_categories = categories_page.find_all('div', {'class':'department'})

        display_log(Fore.BLUE, 'Finding store categories')
        # print(main_categories)

        for i, element in enumerate(main_categories):
            if element.find('div', {'class':'department__caption'}) is not None:
                category = str(element.find('h4', {'class':'department__title'}).get_text()).strip()
                next_link = root_url + str(element.find('a')['href']).strip()

                display_log(Fore.YELLOW, '[{}] {}'.format(i, category))
                
                category_spec_page = getHTMLSOUPEDDocument(next_link)

                #Get the total number of pages
                #https://www.checkers.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=1
                pagination_data = int(str(category_spec_page.find('p', {'class':'total-number-of-results pull-right'}).get_text()).replace(' items','').replace(',','').strip())
                page_number = ceil(pagination_data/20)

                display_log(Fore.BLUE, '-> Page number found {}'.format(page_number))
                print('Iterate over all the products')
                
                #Go through the pages
                for k in range(page_number):
                    #https://www.checkers.co.za/c-2413/All-Departments/Food?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page=1
                    addPage = '?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={}'.format(k) if k>0 else ''
                    products_link = next_link + addPage

                    #? Get the products infos
                    products_megadata = getHTMLSOUPEDDocument(products_link).find_all('div', {'class':'item-product'})

                    for j, product in enumerate(products_megadata):
                        try:
                            display_log(Fore.LIGHTRED_EX, '[*] {}% - {}'.format(round(i*100/len(main_categories)),category))
                            display_log(Fore.CYAN, '{}% - {}'.format(round(k*100/page_number),'PAGE'))

                            #Get the name, price and image of the product
                            product_name = str(product.find('h3', {'class':'item-product__name'}).get_text()).strip()
                            product_price = str(product.find('div', {'class':'special-price__price'}).get_text()).strip()
                            product_image = root_url + str(product.find('div', {'class':'item-product__image __image'}).find('img')['src'])
                            product_link = root_url + str(product.find('a')['href']).strip()

                            #Save the model
                            #? SAVE in the db
                            #Compile the whole product data model
                            TMP_DATA_MODEL = {
                                'brand': _SHOP_NAME_,
                                'product_name': product_name,
                                'product_price': product_price,
                                'product_picture': [product_image],
                                'sku': str(product_name).upper().replace(' ','_'),
                                'used_link': product_link,
                                'meta': {
                                    'category': str(category).upper().strip(),
                                    'subcategory': str(category).upper().strip(),
                                    'shop_name': _SHOP_NAME_,
                                    'website_link': root_url,
                                    'description': '',
                                    },
                                    'date_added':  datetime.datetime.today().replace(microsecond=0)
                            }
                            
                            #! filter
                            filterProduct = {
                                'brand': _SHOP_NAME_,
                                'product_name': product_name,
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
                        except Exception as e:
                            print(e)
                            continue

            else:
                display_log(Fore.LIGHTRED_EX, 'Invalid category')


    except Exception as e:
        print(e)


#!DEBUG
launchBot()