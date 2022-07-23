'''
1. Get all the catalogue from Pick n Pay.
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
import uuid

import SaveOrUpdateItem


driver = False
wait = False

client = False
db = False
_SHOP_NAME_ = 'PICK N PAY'

def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)

display_log(Fore.GREEN, 'ROBOT NAME: PNP-BOT')
display_log(Fore.GREEN, _SHOP_NAME_)


def getHTMLDocument(url):
    response = requests.get(url)
    return response.text


def launchBot():
    os.system('clear')
    try:
        shop_fp = 'picknpay8837887322322'

        root_url = 'https://www.pnp.co.za'
        link = 'https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/c/pnpbase'

        #1. Get the fashion's page
        categories_page = BeautifulSoup(getHTMLDocument(link), 'html.parser')
        #List all the subcategories
        main_categories = categories_page.find('div', {'class':'dmht aisles'}).find_all('div', {'class':'col-sm-2 col-xs-4 aisle-tile'})

        display_log(Fore.BLUE, 'Finding store categories')
        
        for i, element in enumerate(main_categories):
            category = str(element.find('h4').get_text()).strip()

            # if category!='Meat, Poultry & Seafood': #!DEBUG
            #     continue

            #https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Milk%2C-Dairy-%26-Eggs/c/milk-dairy-and-eggs-423144840?pageSize=72&q=%3Arelevance&show=Page#
            next_link = root_url + '/pnpstorefront/pnp/en/All-Products/'+ urllib.parse.quote(category) + str(element.find('a')['href']) +'?pageSize=72&q=%3Arelevance'
            #...
            display_log(Fore.CYAN, '{}. {}'.format(i+1, category))

            #Open the sub categories links
            category_essense = BeautifulSoup(getHTMLDocument(next_link), 'html.parser')

            #Get the number of pages
            if category_essense.find('div', {'class':'col-xs-12 col-sm-6 col-md-5 pagination-wrap'}).find('ul', {'class':'pagination'}) is not None or category_essense.find('div', {'class':'col-xs-12 col-sm-6 col-md-5 pagination-wrap'}) is not None:
                pagination_parent = category_essense.find('div', {'class':'col-xs-12 col-sm-6 col-md-5 pagination-wrap'}).find('ul', {'class':'pagination'}).find_all('li') if category_essense.find('div', {'class':'col-xs-12 col-sm-6 col-md-5 pagination-wrap'}).find('ul', {'class':'pagination'}) is not None else []
                if len(pagination_parent) > 0 : pagination_parent.pop()

                page_number = 1 if category_essense.find('div', {'class':'col-xs-12 col-sm-6 col-md-5 pagination-wrap'}).find('ul', {'class':'pagination'}) is None else  str(pagination_parent[len(pagination_parent)-1].get_text()).strip()

                display_log(Fore.BLUE, '-> Page number found {}'.format(page_number))
                print('Iterate over all the products')

                for j in range(int(page_number)):
                    pageAddition = '&page={}'.format(j) if j>0 else ''
                    #Catalogue link
                    catalogue_link = next_link + pageAddition

                    #? Pull all the products
                    products_essence = BeautifulSoup(getHTMLDocument(catalogue_link), 'html.parser')
                    #? Get the products
                    products_data = products_essence.find('ul', {'class':'col-md-12 product-listing product-grid product-grid'}).find_all('div', {'class':'productCarouselItemContainer'})

                    #Get individual products
                    for index, product in enumerate(products_data):
                        #Get the product link
                        product_link = root_url + str(product.find('a', {'class':'js-potential-impression-click'})['href'])
                        #Get the product's page
                        product_detailed_data = BeautifulSoup(getHTMLDocument(product_link), 'html.parser')
                        #? Get the name, price and images
                        if product_detailed_data.find('div', {'class':'fed-pdp-product-details-title'}) is not None:
                            product_name = str(product_detailed_data.find('div', {'class':'fed-pdp-product-details-title'}).get_text()).strip()
                            display_log(Fore.CYAN, '{}% - {}'.format(round(i*100/len(main_categories)),category))
                            display_log(Fore.YELLOW,'{}% - {}'.format(round(index*100/len(products_data)),product_name))

                            
                            product_price = 'R' + str(float(str(product_detailed_data.find('div', {'class':'normalPrice'}).get_text()).strip().replace('R','').replace(',',''))/100)
                            # product_barcode = str(product_detailed_data.find(text=re.compile('Barcode')).parent())
                            #Get the images
                            images_data = product_detailed_data.find_all('img', {'class':'owl-lazy'})
                            products_images_summary = []

                            for image in images_data:
                                try:
                                    tmp = image['data-zoom-image']
                                    products_images_summary.append(tmp)
                                except:
                                    continue
                            
                            #...
                            try:
                                products_images_summary = products_images_summary[0] if isinstance(products_images_summary[0], list) else products_images_summary
                            except:
                                print('Unarray list of images - All good!')
                                products_images_summary = []
                            
                            #! Determine the sku
                            sku = product_link
                            try:
                                sku = product_link.split('/')[len(product_link.split('/'))-1]
                            except:
                                print('Unable to determine the sku - fallback to product name')
                                sku = product_name.replace(' ', '_').lower()

                            #Compile the whole product data model
                            TMP_DATA_MODEL = {
                                '_id': str(uuid.uuid4()),
                                'shop_fp': shop_fp,
                                'brand': _SHOP_NAME_,
                                'product_name': product_name,
                                'product_price': product_price,
                                'product_picture': products_images_summary,
                                'sku': sku,
                                'used_link': product_link,
                                'meta': {
                                    'category': str(category).upper().strip(),
                                    'subcategory': str(category).upper().strip(),
                                    'shop_name': _SHOP_NAME_,
                                    'website_link': root_url
                                },
                                'date_added':  datetime.datetime.today().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                'date_updated':  datetime.datetime.today().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            }


                            #?Save
                            SaveOrUpdateItem.saveOrUpdateItem(TMP_DATA_MODEL=TMP_DATA_MODEL)
                        print('----------')


    except Exception as e:
        print(e)
        print('Failure detected, relaunching the bot.')
        launchBot()

#! DEBUG
launchBot()