'''
1. Get all the catalogue from KFC
'''
# prettier-ignore
import sys
sys.path.append('../')
import uuid
from boto3.dynamodb.conditions import Key, Attr
import GetUrlDocument
import boto3
import json
import http.client
from scrapingant_client import ScrapingAntClient
import datetime
from colorama import Back, Fore, Style, init
import requests
from bs4 import BeautifulSoup
import re
import csv
from tqdm import tqdm
from ast import Try
from tkinter import E
from unicodedata import category
from numpy import disp
from pymongo import MongoClient
import time
from random import randint
import sys
import os
import traceback
init()

dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-west-1')

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
        collection_catalogue = dynamodb.Table('Catalogues')
        shop_fp = 'kfc9537807322322'

        payload = "{ \"url\": \"https://order.kfc.co.za/menu/bucket\"}"

        soup = GetUrlDocument.getHTMLSOUPEDDocument(
            "https://order.kfc.co.za/menu/bucket")
        # #List all the vailable deals and iterate
        parent_data = soup.find_all('div', {"class": "menu-list ng-scope"})

        for j, product in enumerate(parent_data):
            # ?1. Get the category name
            category = str(product.find(
                'h2', {"class": "ng-binding"}).get_text()).strip()

            if category in _DEALS_AUTHORISED:
                try:
                    display_log(
                        Fore.YELLOW, '[{}]. {}'.format(j + 1, category))
                    #! Go through the indiviual products
                    meals_types = product.find_all('div', {"class": "ng-isolate-scope meal-type"}) if len(product.find_all('div', {
                        "class": "ng-isolate-scope meal-type"})) > 0 else product.find_all('div', {"class": "meal-type ng-isolate-scope"})

                    for k, meal in enumerate(meals_types):
                        # Extract the picture, name, price and id?
                        meal_name = str(meal.find(
                            'div', {"class": "product-name-desc"}).find_all('div')[0].get_text()).strip()
                        meal_price = str(meal.find(
                            'div', {"class": "product-name-desc"}).find_all('div')[1].get_text()).strip()
                        meal_picture = 'https://order.kfc.co.za/' + \
                            str(meal.find(
                                'div', {"class": "product-item-img"}).find('img')['src']).strip()
                        # ? SAVE in the db
                        # Compile the whole product data model
                        TMP_DATA_MODEL = {
                            'id': str(uuid.uuid4()),
                            'shop_fp': shop_fp,
                            'brand': _SHOP_NAME_,
                            'product_name': meal_name,
                            'product_price': meal_price,
                            'product_picture': meal_picture,
                            'sku': str(meal_name).upper(),
                            'used_link': 'https://order.kfc.co.za/menu/bucket',
                            'category': str(category).upper().strip(),
                            'subcategory': str(category).upper().strip(),
                            'shop_name': _SHOP_NAME_,
                            'website_link': 'https://order.kfc.co.za/',
                            'createdAt': datetime.datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            'updatedAt': datetime.datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
                        }

                        # ? 1. Check if the item was already catalogued
                        ipoItemCatalogued = collection_catalogue.query(
                            IndexName='sku-index',
                            KeyConditionExpression=Key(
                                'sku').eq(TMP_DATA_MODEL['sku']),
                            FilterExpression=Attr('product_name').eq(
                                TMP_DATA_MODEL['product_name'])
                        )['Items']

                        if len(ipoItemCatalogued) > 0:  # ? Item was already catalogued
                            ipoItemCatalogued = ipoItemCatalogued[0]
                            # ? 2. Prices already updated
                            # ? 3. Merge and unify the product pictures
                            #! Fix incorrect [[image_link]] format to [image_link]
                            TMP_DATA_MODEL['product_picture'] = [TMP_DATA_MODEL['product_picture']] if isinstance(
                                TMP_DATA_MODEL['product_picture'][0], str) else TMP_DATA_MODEL['product_picture']
                            #!---
                            TMP_DATA_MODEL['product_picture'] += ipoItemCatalogued['product_picture']
                            TMP_DATA_MODEL['product_picture'] = [
                                s for s in TMP_DATA_MODEL['product_picture'] if len(s) > 1]
                            # ? 4. Update the date updated
                            TMP_DATA_MODEL['updatedAt'] = TMP_DATA_MODEL['createdAt']
                            TMP_DATA_MODEL['createdAt'] = ipoItemCatalogued['createdAt']
                            #! Keep the same id
                            TMP_DATA_MODEL['id'] = ipoItemCatalogued['id']

                            # ? SAVE
                            collection_catalogue.put_item(
                                Item=TMP_DATA_MODEL
                            )
                            display_log(
                                Fore.YELLOW, 'Item updated - {}'.format(TMP_DATA_MODEL['sku']))
                            print(TMP_DATA_MODEL)

                        else:  # ? New item
                            display_log(
                                Fore.YELLOW, 'New item detected - {}'.format(TMP_DATA_MODEL['sku']))
                            collection_catalogue.put_item(
                                Item=TMP_DATA_MODEL
                            )
                            print(TMP_DATA_MODEL)
                    print('----------')
                except Exception as e:
                    print("An error occurred:", str(e))
                    traceback.print_exc()
            else:
                display_log(
                    Fore.RED, 'Unauthorised package [{}]'.format(category))

    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()


#!Debug
launchBot()
