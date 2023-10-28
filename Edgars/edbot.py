'''
1. Get all the catalogue from Edgars.
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
import uuid
import SaveOrUpdateItem
import json
import GetUrlDocument


driver = False
wait = False

client = False
db = False
_SHOP_NAME_ = 'EDGARS'


def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)


display_log(Fore.GREEN, 'ROBOT NAME: NEJ')
display_log(Fore.GREEN, _SHOP_NAME_)


def launchBot():
    try:
        os.system('clear')
        link = 'https://www.edgars.co.za/'

        # 1. Get the fashion's page
        fashion_page = BeautifulSoup(
            GetUrlDocument.getHTMLDocument(link + 'fashion'), 'html.parser')
        # List all the subcategories for Fashion
        main_categories = fashion_page.find_all(
            "div", {"class": "pagebuilder-column"})

        display_log(Fore.BLUE, 'Finding store categories')
        for i, element in enumerate(main_categories):
            if element.div != None and element.div.strong != None:
                category = str(element.div.strong.get_text()).replace(
                    'SHOP ', '').strip().upper()
                tmpText = category.lower()
                tmpLink = link + 'fashion/' + str(tmpText)
                # ---
                display_log(Fore.CYAN, '{}. {}'.format(i + 1, category))
                # 2. Open the sub categories links
                tmpSouped = BeautifulSoup(
                    GetUrlDocument.getHTMLDocument(tmpLink), 'html.parser')
                print(tmpLink)
                openGeneral_subcategories(
                    tmpSouped, category, _SHOP_NAME_, link)
    except:
        launchBot()


# ? Get the subcategories
def openGeneral_subcategories(soupedPage, category, shop_name, website_link):
    main_categories = soupedPage.find_all(
        "div", {"class": "pagebuilder-column"})

    # ? Extract the products
    display_log(Fore.BLUE, 'Finding store sub-categories')
    for i, element in enumerate(main_categories):
        # if element.div != None and element.div.strong != None and element.figure != None:
        if element.div != None and element.div.strong != None and element.figure != None:
            subcategory = str(element.div.strong.get_text())
            link = element.a['href']
            # #!DEBUG
            # if subcategory!='KDS': continue

            display_log(Fore.CYAN, '{}. {}'.format(i + 1, subcategory))

            # tmpText = category.lower()
            # ? Get the products
            if len(link) > 0:
                display_log(Fore.WHITE, '-> {}'.format(link))
                getProductsFor(link, category, shop_name,
                               website_link, subcategory)


# ? Get the products
def getProductsFor(link, category, shop_name, website_link, subcategory):
    souped = BeautifulSoup(GetUrlDocument.getHTMLDocument(link), 'html.parser')
    # all_products = souped.find_all('li', {"class":'item product product-item'})

    # Get the total data page
    data_page = int(souped.find(
        'span', {'class': 'infinite-scrolling load-more-wrapper'})['data-page-count'])
    display_log(Fore.LIGHTYELLOW_EX,
                'Found {} pages for this product'.format(data_page))
    for i in range(data_page):
        checkedProductsLink = link + '&p=' + \
            str(i + 1) if re.search("\?", link) else link + '?p=' + str(i + 1)

        display_log(Fore.LIGHTYELLOW_EX, '[{}] {}'.format(
            i + 1, checkedProductsLink))
        soupedProducts = BeautifulSoup(
            GetUrlDocument.getHTMLDocument(checkedProductsLink), 'html.parser')
        all_products = soupedProducts.find_all(
            'li', {"class": 'item product product-item'})
        # Navigate through all the products
        for j, product in enumerate(all_products):
            if product.find('div', {'class': 'brand'}) != None:
                try:
                    # ? Get the product's link
                    prod_link = product.find(
                        'a', {'class': 'product photo product-item-photo'})['href']
                    print(
                        '{}% - {}'.format(round(j * 100 / len(all_products)), prod_link))
                    # ? Get the meta
                    display_log(
                        Fore.MAGENTA, 'Getting product brand, name and price')
                    brand = product.find('div', {'class': 'brand'}).get_text()
                    product_name = str(product.find(
                        'strong', {'class': 'product name product-item-name'}).get_text()).strip()
                    product_price = str(product.find(
                        'span', {'data-price-type': 'finalPrice'}).get_text()).strip()
                    # ? Get additional pictures
                    display_log(Fore.MAGENTA, 'Getting product pictures')
                    soupedTgProduct = BeautifulSoup(
                        GetUrlDocument.getHTMLDocument(prod_link), 'html.parser')
                    # product_picture = soupedTgProduct.find_all('div',{'class':'gallery-placeholder'})[0].img['src'] #! Take the main one for now
                    product_picture = []

                    image_data = json.loads(str(soupedTgProduct.find_all(
                        'div', {'class': 'product media'})[0].select_one('script').contents[0]))
                    image_data = image_data['[data-gallery-role=gallery-placeholder]']['mage/gallery/gallery']['data']

                    for image in image_data:
                        # Save the picture link
                        product_picture.append(image['full'])

                    # Get the prodcut SKU
                    #! Determine the sku
                    sku = prod_link

                    try:
                        sku = str(soupedTgProduct.find(
                            'td', {'data-th': 'SKU'}).get_text()).strip()
                    except:
                        print(
                            'Unable to determine the sku - fallback to product name')
                        sku = product_name.replace(' ', '_').lower()

                    # Get the item size if any
                    # product_size = soupedTgProduct.find_all('div', {'class':'product-options-wrapper'})[0].find_all('script')[1].text

                    # print(product_size)

                    # Compile the whole product data model
                    shop_fp = 'edgars7737887322322'

                    TMP_DATA_MODEL = {
                        'id': str(uuid.uuid4()),
                        'shop_fp': shop_fp,
                        'brand': brand,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_picture': product_picture,
                        'sku': sku,
                        'used_link': prod_link,
                        'meta': {
                            'category': category,
                            'subcategory': subcategory,
                            'shop_name': shop_name,
                            'website_link': website_link,
                            'options': {}
                        },
                        'date_added': datetime.datetime.today().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'date_updated': datetime.datetime.today().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }

                    # ?Save
                    SaveOrUpdateItem.saveOrUpdateItem(
                        TMP_DATA_MODEL=TMP_DATA_MODEL)
                    # print(TMP_DATA_MODEL)
                except Exception as e:
                    print(e)

                print('\n\n')
            else:  # !error
                print('Invalid product')

        print('\n')


#!Debug start
launchBot()
