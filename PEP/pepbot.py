'''
1. Get all the catalogue from PEP.
'''
# prettier-ignore
from ast import Try
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
import uuid
import GetUrlDocument
import SaveOrUpdateItem

conn = http.client.HTTPSConnection("api.scrapingant.com")


driver = False
wait = False

client = False
db = False
_SHOP_NAME_ = 'PEP'


def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)


display_log(Fore.GREEN, 'ROBOT NAME: PEP-BOT')
display_log(Fore.GREEN, _SHOP_NAME_)

# Create a ScrapingAntClient instance
headers = {
    'x-api-key': "9d1df42476e649968ddb8d58a18cb5c6",
    'content-type': "application/json",
    'accept': "application/json"
}


def launchBot():
    os.system('clear')

    try:
        shop_fp = 'pephome8937557322322'

        link = 'https://www.pepstores.com'
        payload = "{ \"url\": \"https://www.pepstores.com\"}"
        # 1. Get the main page
        conn.request("POST", "/v1/general", payload, headers)

        res = conn.getresponse()
        data = res.read()

        soup = BeautifulSoup(json.loads(data.decode("utf-8"))
                             ['content'], 'html.parser')

        # List all categories
        main_categories = soup.find_all(
            'div', {'class': 'menu-button-component'})
        # print(main_categories)

        # Iterate
        for index, category_node in enumerate(main_categories):
            next_link = link + \
                str(category_node.find(
                    'a', {'class': 'btn btn-light menu-btn'})['href'])
            category = str(category_node.find(
                'a', {'class': 'btn btn-light menu-btn'}).get_text()).strip()

            if category.upper() not in ['MONEY', 'LAY-BY BUDDY', 'CATALOGUES']:

                display_log(Fore.YELLOW, '[{}] {}'.format(index + 1, category))

                # Go through the subcategories
                payload = "{ \"url\": \"" + next_link + "\"}"
                # 1. Get the main page
                conn.request("POST", "/v1/general", payload, headers)

                res = conn.getresponse()
                data = res.read()

                subcategory_data = BeautifulSoup(json.loads(
                    data.decode("utf-8"))['content'], 'html.parser')
                subcategories_all = subcategory_data.find_all(
                    'a', {'class': 'image-content'})

                # ? Go inside the individual sbs
                for i, sub_data in enumerate(subcategories_all):
                    sub_link = link + '/' + str(sub_data['href']).strip()
                    subcategory_name = str(sub_data.get_text()).strip()

                    payload = "{ \"url\": \"" + sub_link + "\"}"
                    # 1. Get the main page
                    conn.request("POST", "/v1/general", payload, headers)

                    res = conn.getresponse()
                    data = res.read()

                    products_data_all = BeautifulSoup(json.loads(
                        data.decode("utf-8"))['content'], 'html.parser')

                    # ? Get the total number of pages
                    pagination_data = products_data_all.find_all(
                        'li', {'class': 'page-item'})

                    pagination_data.pop()
                    page_number = int(
                        pagination_data[len(pagination_data) - 1].get_text())

                    display_log(
                        Fore.BLUE, '-> Page number found {}'.format(page_number))
                    print('Iterate over all the products')

                    # ? Go through the pages
                    for page in range(page_number):
                        # https://www.pepstores.com/products/ladies/outerwear?pageSize=20&currentPage=1
                        addPage = "?pageSize=20&currentPage=" + str(page + 1)
                        products_link = sub_link + addPage

                        payload = "{ \"url\": \"" + products_link + "\"}"
                        # 1. Get the main page
                        conn.request("POST", "/v1/general", payload, headers)

                        res = conn.getresponse()
                        data = res.read()

                        products_megadata = BeautifulSoup(json.loads(
                            data.decode("utf-8"))['content'], 'html.parser')
                        products_mega_infos = products_megadata.find_all(
                            'a', {'class': 'product-content d-flex flex-column'})
                        # ? Get all the products for this page
                        for j, product_l1 in enumerate(products_mega_infos):
                            try:
                                display_log(Fore.LIGHTRED_EX, '[*] {}% - {}'.format(
                                    round(index * 100 / len(main_categories)), category))
                                display_log(
                                    Fore.CYAN, '{}% - {}'.format(round(i * 100 / len(subcategories_all)), subcategory_name))

                                # Get the product's page link
                                product_page_link = link + product_l1['href']

                                # ? Do the final product lookup
                                payload = "{ \"url\": \"" + \
                                    product_page_link + "\"}"
                                # 1. Get the main page
                                conn.request("POST", "/v1/general",
                                             payload, headers)

                                res = conn.getresponse()
                                data = res.read()

                                product_final_data = BeautifulSoup(json.loads(
                                    data.decode("utf-8"))['content'], 'html.parser')

                                # Get the name, price, picture and sizes
                                product_name = str(product_final_data.find(
                                    'div', {'class': 'product-wrapper'}).find('header').find('h1').get_text()).strip()
                                product_price = str(product_final_data.find('div', {
                                                    'class': 'product-wrapper'}).find('span', {'class': 'final-price'}).get_text()).strip()
                                product_image = str(product_final_data.find(
                                    'div', {'class': 'gallery-wrap'}).find('img')['src']).strip()
                                # Get the sizes
                                print(product_page_link)
                                product_sizes_data = product_final_data.find('div', {'class': 'scrollinner'}).find_all(
                                    'button') if product_final_data.find('div', {'class': 'scrollinner'}) is not None else []

                                display_log(
                                    Fore.YELLOW, '{}% - {}'.format(round(j * 100 / len(products_mega_infos)), product_name))

                                product_sizes = []

                                for size in product_sizes_data:
                                    product_sizes.append(
                                        str(size.get_text()).strip())

                                #! Determine the sku
                                sku = product_page_link
                                try:
                                    sku = str(
                                        str(product_name).upper().replace(' ', '_')),
                                except:
                                    print(
                                        'Unable to determine the sku - fallback to product name')
                                    sku = str(product_name.replace(
                                        ' ', '_').lower())

                                # Save the model
                                # ? SAVE in the db
                                # Compile the whole product data model
                                TMP_DATA_MODEL = {
                                    'id': str(uuid.uuid4()),
                                    'shop_fp': shop_fp,
                                    'brand': _SHOP_NAME_,
                                    'product_name': product_name,
                                    'product_price': product_price,
                                    'product_picture': [product_image],
                                    'sku': sku,
                                    'used_link': product_page_link,
                                    'meta': {
                                        'category': str(category).upper().strip(),
                                        'subcategory': str(subcategory_name).upper().strip(),
                                        'shop_name': _SHOP_NAME_,
                                        'website_link': 'https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall',
                                        'description': '',
                                        'options': {
                                            'size': product_sizes
                                        }
                                    },
                                    'date_added': datetime.datetime.today().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    'date_updated': datetime.datetime.today().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                }

                                print(sku)

                                # print(TMP_DATA_MODEL)

                                # ? Save
                                # SaveOrUpdateItem.saveOrUpdateItem(TMP_DATA_MODEL=TMP_DATA_MODEL)
                                print('----------')
                            except Exception as e:
                                print(e)
                                continue

            else:
                print('Unauthorised category')

    except Exception as e:
        print(e)
        launchBot()


#! Debug
launchBot()
