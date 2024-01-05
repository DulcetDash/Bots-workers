'''
1. Get all the catalogue from Debonairs
'''
# prettier-ignore
import sys
sys.path.append('../')
import Utility
import SaveOrUpdateItem
import ImageDownloader
import GetUrlDocument
from ast import Try
from cmath import pi
from tkinter import E
from unicodedata import category
from numpy import disp
import time
from random import randint
from tqdm import tqdm
import csv
import re
from bs4 import BeautifulSoup
import requests
from colorama import Back, Fore, Style, init
init()
import datetime
import http.client
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid

dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-west-1')

conn = http.client.HTTPSConnection("api.scrapingant.com")


driver = False
wait = False

client = False
db = False
_SHOP_NAME_ = 'DEBONAIRS'

category_map = {
    "NEW CHEEZY RANGE": 85934,
    "MEAT PIZZAS": 85099,
    "CHICKEN PIZZAS": 85106,
    "VEGETARIAN PIZZAS": 85112,
    "SPECIALITY PIZZAS": 85123,
    "SIDES": 85118,
    "DRINKS": 85140
}


def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)


display_log(Fore.GREEN, 'ROBOT NAME: DEBOBOT')
display_log(Fore.GREEN, _SHOP_NAME_)


def getHTMLDocument(url):
    response = requests.get(url)
    return response.text


def launchBot():
    _INDEX_START_MENU_ITEM_ = 85099

    try:
        shop_fp = 'debonairs97639807992322'

        soup = GetUrlDocument.getHTMLSOUPEDDocument(
            'https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall')

        # List all the categories of pizzas
        pizzas_categories = soup.find_all('div', {'class': 'm__listing'})

        for index, parent_set in enumerate(pizzas_categories):
            # Get the name of the category
            category = str(parent_set.find('div', {
                           "class": 'm__listing__category-title--text'}).find('h2').get_text()).replace("\"", "").strip()
            # Get the details of each pizzas
            pizzas_targeted_set = parent_set.find_all(
                'div', {'class': 'm-list-item'})

            display_log(Fore.YELLOW, '[{}] {}'.format(index + 1, category))

            #! Exclude some categories from the complex process
            if category in [
                # 'Meat Pizzas', 'Chicken Pizzas', 'Vegetarian Pizzas', 'New Cheezy Range', 
                'Speciality Pizzas']:
                 #TODO: Debug
                _INDEX_START_MENU_ITEM_ = category_map[category.upper()]

                for j, pizza_type in enumerate(pizzas_targeted_set):
                    # Get the pizza name for linking
                    pizza_name = str(pizza_type.find(
                        'h3', {'class': 'm-list-item__name'}).get_text()).replace("\"", "").strip()
                    pizza_price = str(pizza_type.find(
                        'p', {'class': 'm-list-item__price'}).get_text()).replace('+', '').strip()

                    currency, price = Utility.extract_currency_and_price(pizza_price)

                    pizza_price = price
                    pizza_currency = currency

                    # ? Create the modal link
                    # item_number = _INDEX_START_MENU_ITEM_
                    # # https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/55553/garlic-bacon-%E2%80%98n-jalape%C3%B1o-(new)
                    pizza_name_asURL = str(
                        pizza_name).lower().strip().replace(' ', '-')

                    # _INDEX_START_MENU_ITEM_ = 55572 if pizza_name_asURL is 'custard-malva-pudding-(new)' else _INDEX_START_MENU_ITEM_

                    # item_number = 80383 if pizza_name_asURL is 'on-the-double®' else 55570 if pizza_name_asURL is 'on-the-double®-feast' else 80402 if pizza_name_asURL is 'on-the-triple®' else 55571 if pizza_name_asURL is 'on-the-triple®-feast' else _INDEX_START_MENU_ITEM_
                    # # print(pizza_name_asURL)

                    item_number = _INDEX_START_MENU_ITEM_

                    # print("https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/" + str(
                    #         item_number) + "/" + pizza_name_asURL)
                    
                    # _INDEX_START_MENU_ITEM_ += 1

                    # continue

                    #! Exlude: on the double/triple
                    if pizza_name_asURL not in ['on-the-double®', 'on-the-double®-feast', 'on-the-triple®', 'on-the-triple®-feast']:
                        print('{} -> {}'.format(item_number, pizza_name_asURL))

                        if True:
                            soupPizza = GetUrlDocument.getHTMLSOUPEDDocument("https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/" + str(
                            item_number) + "/" + pizza_name_asURL)

                            print("https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/" + str(
                            item_number) + "/" + pizza_name_asURL)

                            # ? Extract the name, description, picture and options
                            name = soupPizza.find(
                                'div', {'class': 'mi__description'}).find('h1').get_text()

                            pizza_description = soupPizza.find(
                                'div', {'class': 'mi__description'}).find('p').get_text()
                            pizza_image = str(soupPizza.find(
                                'div', {'class': 'd-image__container mi__img'})['data-for-url']).strip() if soupPizza.find(
                                'div', {'class': 'd-image__container mi__img'}) != None else 'Placeholder'
                            # get the options
                            options_set = soupPizza.find('div', {'class': 'mi__option_parent'}).find(
                                'div', {'class': 'mi__option'})

                            # ? Get the pizza size options
                            options_domain = options_set.find(
                                'div').find('ul').find_all('li')
                            
                            pizza_size_price_2 = None
                            
                            _ , pizza_size_price_0 = Utility.extract_currency_and_price(str(options_domain[0].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())
                            _ , pizza_size_price_1 = Utility.extract_currency_and_price(str(options_domain[1].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())

                            if options_domain[2].find('span', {'class': 'mi__option-price'}) != None:
                                _ , pizza_size_price_2 = Utility.extract_currency_and_price(str(options_domain[2].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())

                            pizza_size = [
                                {
                                    'name': str(options_domain[0].find('label').get_text()).replace('+', '').strip(),
                                    'price': pizza_size_price_0
                                },
                                {
                                    'name': str(options_domain[1].find('label').get_text()).replace('+', '').strip(),
                                    'price': pizza_size_price_1
                                }
                            ]

                            if pizza_size_price_2 != None:
                                pizza_size.append({
                                     'name': str(options_domain[2].find('label').get_text()).replace('+', '').strip(),
                                    'price': pizza_size_price_2
                                })

                            # ? Get the base, cheese and extra toppings details
                            other_options_domain = None
                            has_other_options = False

                            # Check if the third item in options_domain has the required div
                            if options_domain[3].find('div', {'class': 'mi__radio_parent'}) is not None:
                                div = options_domain[3].find('div', {'class': 'mi__radio_parent'}).find('div')
                                if div is not None:
                                    has_other_options = True

                            # Check if the second item in options_domain has the required div
                            if options_domain[2].find('div', {'class': 'mi__radio_parent'}) is not None:
                                div = options_domain[2].find('div', {'class': 'mi__radio_parent'}).find('div')
                                if div is not None:
                                    has_other_options = True

                            if has_other_options:
                                div_3 = options_domain[3].find('div', {'class': 'mi__radio_parent'})
                                div_2 = options_domain[2].find('div', {'class': 'mi__radio_parent'})

                                if div_3 is not None and div_3.find('div') is not None:
                                    other_options_domain = div_3.find('div').find_all('div', {'class': 'mi__option'})
                                elif div_2 is not None and div_2.find('div') is not None:
                                    other_options_domain = div_2.find('div').find_all('div', {'class': 'mi__option'})
                                else:
                                    other_options_domain = None


                                if other_options_domain != None and len(other_options_domain) >0:
                                    # 1. Base
                                    base_data = other_options_domain[0].find(
                                        'div').find('ul').find_all('li')
                                    
                                    _ , pizza_base_price_0 = Utility.extract_currency_and_price(str(base_data[0].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())
                                    _ , pizza_base_price_1 = Utility.extract_currency_and_price(str(base_data[1].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())

                                    pizza_base_price_2 = None
                                    pizza_base_price_3 = None

                                    if base_data[2].find('span', {'class': 'mi__option-price'})!=None:
                                        _ , pizza_base_price_2 = Utility.extract_currency_and_price(str(base_data[2].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())
                                        _ , pizza_base_price_3 = Utility.extract_currency_and_price(str(base_data[3].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())


                                    pizza_base = [
                                        {
                                            'name': str(base_data[0].find('label').get_text()).replace('+', '').strip(),
                                            'price': pizza_base_price_0
                                        },
                                        {
                                            'name': str(base_data[1].find('label').get_text()).replace('+', '').strip(),
                                            'price': pizza_base_price_1
                                        }
                                    ]

                                    if pizza_base_price_2 != None:
                                        pizza_base.append({
                                            'name': str(base_data[2].find('label').get_text()).replace('+', '').strip(),
                                            'price': pizza_base_price_2
                                        })
                                        pizza_base.append({
                                            'name': str(base_data[3].find('label').get_text()).replace('+', '').strip(),
                                            'price': pizza_base_price_3
                                        })
                                else:
                                    other_options_domain = options_domain
                            else:
                                other_options_domain = options_domain[1].find('div', {'class': 'mi__radio_parent'}).find('div').find_all('div', {'class': 'mi__option'}) if len( options_domain) > 0 else options_domain[0].find('div', {'class': 'mi__radio_parent'}).find('div').find_all('div', {'class': 'mi__option'})

                            # 2. Cheese
                            cheese_data = other_options_domain[1].find(
                                'div').find('ul').find_all('li') if other_options_domain[1].find(
                                'div') !=None else other_options_domain
                            
                            pizza_cheese_price_0 = None
                            pizza_cheese_price_1 = None
                            
                            if cheese_data[0].find('span', {'class': 'mi__option-price'})!=None:
                                _ , pizza_cheese_price_0 = Utility.extract_currency_and_price(str(cheese_data[0].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())
                                _ , pizza_cheese_price_1 = Utility.extract_currency_and_price(str(cheese_data[1].find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())

                            pizza_cheese = [
                                {
                                    'name': str(cheese_data[0].find('label').get_text()).replace('+', '').strip(),
                                    'price': pizza_cheese_price_0
                                },
                                {
                                    'name': str(cheese_data[1].find('label').get_text()).replace('+', '').strip(),
                                    'price': pizza_cheese_price_1
                                }
                            ] if pizza_cheese_price_0!=None else []

                            # 3. Extra toppings and sauce
                            extra_toppings_data = other_options_domain[2].find(
                                'div').find('ul').find_all('li') if other_options_domain[2].find(
                                'div').find('ul') !=None else None

                            # print(extra_toppings_data)
                            pizza_toppings = []

                            if extra_toppings_data!=None:
                                for index, topping in enumerate(extra_toppings_data):
                                    if topping.find('span', {'class': 'mi__option-price'}) == None: continue

                                    _ , topping_price = Utility.extract_currency_and_price(str(topping.find('span', {'class': 'mi__option-price'}).get_text()).replace('+', '').strip())

                                    tmpData = {
                                        'name': str(topping.find('label').get_text()).replace('+', '').strip(),
                                        'price': topping_price
                                    }
                                    # ...
                                    pizza_toppings.append(tmpData)

                            # Download the image to the Image Repository
                            productId = str(uuid.uuid4())
                            sku = str(name).upper().replace(' ', '_')
                            newProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=pizza_image, storeId=shop_fp, productId=productId, sku=sku, useProxy=False)

                            # ? SAVE in the db
                            # Compile the whole product data model
                            TMP_DATA_MODEL = {
                                'id': productId,
                                'shop_fp': shop_fp,
                                'brand': _SHOP_NAME_,
                                'product_name': name,
                                'product_price': pizza_price,
                                'currency': pizza_currency,
                                'product_picture': [newProductImage],
                                'sku': sku,
                                'used_link': "https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/" + str(item_number) + "/" + pizza_name_asURL,
                                'category': str(category).upper().strip(),
                                'subcategory': str(category).upper().strip(),
                                'shop_name': _SHOP_NAME_,
                                'website_link': 'https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall',
                                'description': pizza_description,
                                'options': {
                                    'size': pizza_size,
                                    'base': pizza_base,
                                    'cheese': pizza_cheese,
                                    'extra toppings and sauces': pizza_toppings
                                },
                                'createdAt': int(time.time()) * 1000,
                                'updatedAt': int(time.time()) * 1000
                            }

                            SaveOrUpdateItem.saveOrUpdateItem(TMP_DATA_MODEL=TMP_DATA_MODEL)
                        print('----------')

                    else:
                        display_log(Fore.RED, 'Some encoding is wrong.')

                    #! Keep going with the item number - crucial
                    _INDEX_START_MENU_ITEM_ += 1
                    # break
                # break

            else:  # ? Some simpler categories
                if category in ['Sides']:
                     #TODO: Debug
                    _INDEX_START_MENU_ITEM_ = category_map[category.upper()]

                    # Get the details of each pizzas
                    pizzas_targeted_set = parent_set.find_all(
                        'div', {'class': 'm-list-item'})
                    for j, pizza_type in enumerate(pizzas_targeted_set):
                        # Get the pizza name for linking
                        pizza_name = str(pizza_type.find(
                            'h3', {'class': 'm-list-item__name'}).get_text()).replace("\"", "").strip()
                        pizza_price = str(pizza_type.find(
                            'p', {'class': 'm-list-item__price'}).get_text()).replace('+', '').strip()
                        
                        currency, price = Utility.extract_currency_and_price(pizza_price)

                        pizza_price = price

                        # ? Create the modal link
                        item_number = _INDEX_START_MENU_ITEM_
                        # https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/55553/garlic-bacon-%E2%80%98n-jalape%C3%B1o-(new)
                        pizza_name_asURL = str(
                            pizza_name).lower().strip().replace(' ', '-')

                        # _INDEX_START_MENU_ITEM_ = 55572 if pizza_name_asURL is 'custard-malva-pudding-(new)' else _INDEX_START_MENU_ITEM_

                        # item_number = 80383 if pizza_name_asURL is 'on-the-double®' else 55570 if pizza_name_asURL is 'on-the-double®-feast' else 80402 if pizza_name_asURL is 'on-the-triple®' else 55571 if pizza_name_asURL is 'on-the-triple®-feast' else _INDEX_START_MENU_ITEM_

                        #! Exlude: on the double/triple
                        if pizza_name_asURL not in ['on-the-double®', 'on-the-double®-feast', 'on-the-triple®', 'on-the-triple®-feast']:
                            print('{} -> {}'.format(item_number, pizza_name_asURL))

                            if True:
                                soupPizza = GetUrlDocument.getHTMLSOUPEDDocument("https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/" + str(
                                item_number) + "/" + pizza_name_asURL)

                                # ? Extract the name, description, picture and options
                                name = soupPizza.find(
                                    'div', {'class': 'mi__description'}).find('h1').get_text()
                                pizza_description = soupPizza.find(
                                    'div', {'class': 'mi__description'}).find('p').get_text()
                                pizza_image = str(soupPizza.find(
                                    'div', {'class': 'd-image__container mi__img'})['data-for-url']).strip() if soupPizza.find(
                                    'div', {'class': 'd-image__container mi__img'}) != None else 'Placeholder'

                                # Download the image to the Image Repository
                                productId = str(uuid.uuid4())
                                sku = str(name).upper().replace(' ', '_')
                                newProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=pizza_image, storeId=shop_fp, productId=productId, sku=sku, useProxy=False)

                                # ? SAVE in the db
                                # Compile the whole product data model
                                TMP_DATA_MODEL = {
                                    'id': productId,
                                    'shop_fp': shop_fp,
                                    'brand': _SHOP_NAME_,
                                    'product_name': name,
                                    'product_price': pizza_price,
                                    'currency': currency,
                                    'product_picture': [newProductImage],
                                    'sku': sku,
                                    'used_link': "https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/" + str(item_number) + "/" + pizza_name_asURL,
                                    'category': str(category).upper().strip(),
                                    'subcategory': str(category).upper().strip(),
                                    'shop_name': _SHOP_NAME_,
                                    'website_link': 'https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall',
                                    'description': pizza_description,
                                    'options': {},
                                    'createdAt': int(time.time()) * 1000,
                                    'updatedAt': int(time.time()) * 1000
                                }

                                SaveOrUpdateItem.saveOrUpdateItem(TMP_DATA_MODEL=TMP_DATA_MODEL)
                                
                            print('----------')

                        #! Keep going with the item number - crucial
                        _INDEX_START_MENU_ITEM_ += 1

                elif category in ['Drinks']:
                     #TODO: Debug
                    _INDEX_START_MENU_ITEM_ = category_map[category.upper()]

                    # Get the details of each pizzas
                    pizzas_targeted_set = parent_set.find_all(
                        'div', {'class': 'm-list-item'})
                    for j, pizza_type in enumerate(pizzas_targeted_set):
                        # Get the pizza name for linking
                        pizza_name = str(pizza_type.find(
                            'h3', {'class': 'm-list-item__name'}).get_text()).replace("\"", "").strip()
                        pizza_price = str(pizza_type.find(
                            'p', {'class': 'm-list-item__price'}).get_text()).replace('+', '').strip()

                        currency, price = Utility.extract_currency_and_price(pizza_price)

                        pizza_price = price

                        # ? Create the modal link
                        item_number = _INDEX_START_MENU_ITEM_
                        # https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/55553/garlic-bacon-%E2%80%98n-jalape%C3%B1o-(new)
                        pizza_name_asURL = str(
                            pizza_name).lower().strip().replace(' ', '-')
                        
                        # item_number = 80425 if pizza_name_asURL in '500ml-buddy' else 80426 if pizza_name_asURL in '2l-softdrink' else 80427 if pizza_name_asURL in 'water' else _INDEX_START_MENU_ITEM_
                        # _INDEX_START_MENU_ITEM_ = item_number

                        #! Exlude: on the double/triple
                        if pizza_name_asURL not in ['on-the-double®', 'on-the-double®-feast', 'on-the-triple®', 'on-the-triple®-feast']:
                            print('{} -> {}'.format(item_number, pizza_name_asURL))

                            if True:
                                soupPizza = GetUrlDocument.getHTMLSOUPEDDocument("https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/" + str(
                                item_number) + "/" + pizza_name_asURL)

                                # ? Extract the name, description, picture and options
                                name = soupPizza.find(
                                    'div', {'class': 'mi__description'}).find('h1').get_text()
                                pizza_description = soupPizza.find(
                                    'div', {'class': 'mi__description'}).find('p').get_text()
                                pizza_image = 'placeholder'

                                # get the options
                                options_set = soupPizza.find(
                                    'div', {'class': 'mi__option_parent'})

                                # ? Get the pizza size options
                                options_domain = options_set.find(
                                    'ul').find_all('li', {'class': 'mi__radio'})

                                options_summary = []

                                for l, option in enumerate(options_domain):
                                    _, optionPrice = Utility.extract_currency_and_price(str(option.find('span', {'class': 'mi__option-price'}).get_text()).strip())

                                    tmpOptionData = {
                                        'name': str(option.find('label').get_text()).strip(),
                                        'price': optionPrice
                                    }
                                    # Save
                                    options_summary.append(tmpOptionData)

                                
                                # Download the image to the Image Repository
                                productId = str(uuid.uuid4())
                                sku = str(name).upper().replace(' ', '_')
                                newProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=pizza_image, storeId=shop_fp, productId=productId, sku=sku, useProxy=False)

                                # ? SAVE in the db
                                # Compile the whole product data model
                                TMP_DATA_MODEL = {
                                    'id': productId,
                                    'shop_fp': shop_fp,
                                    'brand': _SHOP_NAME_,
                                    'product_name': name,
                                    'product_price': pizza_price,
                                    'currency': currency,
                                    'product_picture': [newProductImage],
                                    'sku': sku,
                                    'used_link': "https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall/menu-item/" + str(item_number) + "/" + pizza_name_asURL,
                                    'category': str(category).upper().strip(),
                                    'subcategory': str(category).upper().strip(),
                                    'shop_name': _SHOP_NAME_,
                                    'website_link': 'https://app.debonairspizza.co.na/restaurant/8/debonairs-pizza-maerua-mall',
                                    'description': pizza_description,
                                    'options': options_summary,
                                    'createdAt': int(time.time()) * 1000,
                                    'updatedAt': int(time.time()) * 1000
                                }

                                SaveOrUpdateItem.saveOrUpdateItem(TMP_DATA_MODEL=TMP_DATA_MODEL)
                            print('----------')

                        #! Keep going with the item number - crucial
                        _INDEX_START_MENU_ITEM_ += 1
                else:  # Not accepted categories
                    print('Not accepted categories -> {}'.format(category))
                    #! Keep going with the item number - crucial
                    _INDEX_START_MENU_ITEM_ += 1

    except Exception as e:
        print(e.with_traceback())


#!Debug
launchBot()
