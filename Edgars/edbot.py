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


def getHTMLDocument(url):
    response = requests.get(url)
    return response.text


def launchBot():
    link = 'https://www.edgars.co.za/'

    #1. Get the fashion's page
    fashion_page = BeautifulSoup(getHTMLDocument(link + 'fashion'), 'html.parser')
    #List all the subcategories for Fashion
    main_categories = fashion_page.find_all("div", {"class":"pagebuilder-column"})
    
    display_log(Fore.BLUE, 'Finding store categories')
    for i,element in enumerate(main_categories):
        if element.div != None and element.div.strong != None:
            category = str(element.div.strong.get_text()).replace('SHOP ', '').strip().upper()
            tmpText = category.lower()
            tmpLink = link + 'fashion/' + str(tmpText)
            #---
            display_log(Fore.CYAN, '{}. {}'.format(i+1, category))
            #2. Open the sub categories links
            tmpSouped = BeautifulSoup(getHTMLDocument(tmpLink), 'html.parser')
            print(tmpLink)
            openGeneral_subcategories(tmpSouped, category, _SHOP_NAME_, link)


#? Get the subcategories
def openGeneral_subcategories(soupedPage, category, shop_name, website_link):
    main_categories = soupedPage.find_all("div", {"class":"pagebuilder-column"})
    
    #? Extract the products
    display_log(Fore.BLUE, 'Finding store sub-categories')
    for i,element in enumerate(main_categories):
        # if element.div != None and element.div.strong != None and element.figure != None:
        if element.div != None and element.div.strong != None and element.figure != None:
            subcategory = str(element.div.strong.get_text())
            link = element.a['href']
            display_log(Fore.CYAN, '{}. {}'.format(i+1, subcategory))
            # tmpText = category.lower()
            #? Get the products
            if len(link) > 0:
                display_log(Fore.WHITE, '-> {}'.format(link))
                getProductsFor(link, category, shop_name, website_link, subcategory)
                


#? Get the products
def getProductsFor(link, category, shop_name, website_link, subcategory):
    souped = BeautifulSoup(getHTMLDocument(link), 'html.parser')
    # all_products = souped.find_all('li', {"class":'item product product-item'})

    #Get the total data page
    data_page = int(souped.find('span', {'class':'infinite-scrolling load-more-wrapper'})['data-page-count'])
    display_log(Fore.LIGHTYELLOW_EX, 'Found {} pages for this product'.format(data_page))
    for i in range(data_page):
        display_log(Fore.LIGHTYELLOW_EX, '[{}] {}'.format(i+1, link + '?p=' + str(i+1)))
        soupedProducts = BeautifulSoup(getHTMLDocument(link + '?p=' + str(i+1)), 'html.parser')
        all_products = soupedProducts.find_all('li', {"class":'item product product-item'})
        #Navigate through all the products
        for j, product in enumerate(all_products):
            if product.find('div', {'class':'brand'}) != None:
                try:
                    #? Get the product's link
                    prod_link = product.find('a', {'class':'product photo product-item-photo'})['href']
                    print('{}% - {}'.format(round(j*100/len(all_products)),prod_link))
                    #? Get the meta
                    display_log(Fore.MAGENTA, 'Getting product brand, name and price')
                    brand =  product.find('div', {'class':'brand'}).get_text()
                    product_name = str(product.find('strong', {'class':'product name product-item-name'}).get_text()).strip()
                    product_price = str(product.find('span', {'data-price-type':'finalPrice'}).get_text()).strip()
                    #? Get additional pictures
                    display_log(Fore.MAGENTA, 'Getting product pictures')
                    soupedTgProduct = BeautifulSoup(getHTMLDocument(prod_link), 'html.parser')
                    product_picture = soupedTgProduct.find_all('div',{'class':'gallery-placeholder'})[0].img['src'] #! Take the main one for now
                    #Get the prodcut SKU
                    sku = str(soupedTgProduct.find('td', {'data-th':'SKU'}).get_text()).strip()
                    #Compile the whole product data model
                    TMP_DATA_MODEL = {
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
                            'website_link': website_link
                        },
                        'date_added':  datetime.datetime.today().replace(microsecond=0)
                    }

                
                    client = MongoClient(
                    'mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')

                    db = client.NEJ
                    collection_catalogue = db['catalogue_central']

                    #? DONE - save
                    #! Block duplicate
                    checkUnicity = collection_catalogue.find({
                        'brand': brand,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_picture': product_picture,
                        'sku': sku,
                        'meta.category': category,
                        'meta.subcategory': subcategory,
                        'meta.shop_name': shop_name
                    })

                    if checkUnicity.count() <= 0: #?new
                        print(TMP_DATA_MODEL)
                        display_log(Fore.GREEN, 'Saving the product model in catalogue')
                        collection_catalogue.insert_one(TMP_DATA_MODEL)
                    else: #! Already added
                        display_log(Fore.RED, 'This product was already processed.')
                except Exception as e:
                    print(e)

                print('\n\n')
            else: #!error
                print('Invalid product')
            
        print('\n')

#!Debug start
launchBot()