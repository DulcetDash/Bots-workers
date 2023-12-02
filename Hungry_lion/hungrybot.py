'''
1. Get all the catalogue from Hungry lion
'''
# prettier-ignore
import sys
sys.path.append('../')
import Utility
import SaveOrUpdateItem
import ImageDownloader
from ast import Try
from cmath import pi
from tkinter import E
from unicodedata import category
from numpy import disp
import time
from random import randint
from bs4 import BeautifulSoup
import requests
from colorama import Back, Fore, Style, init
init()
import http.client
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-west-1')

conn = http.client.HTTPSConnection("api.scrapingant.com")


driver = False
wait = False

client = False
db = False
_SHOP_NAME_ = 'HUNGRY LION'


def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)


display_log(Fore.GREEN, 'ROBOT NAME: HUNGRYBOT')
display_log(Fore.GREEN, _SHOP_NAME_)

# Create a ScrapingAntClient instance
headers = {
    'x-api-key': "53ea95eb0dd346f9a53ba3188a41a29e",
    'content-type': "application/json",
    'accept': "application/json"
}


def getHTMLSOUPEDDocument(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def launchBot():
    try:
        collection_catalogue = dynamodb.Table('Catalogues')
        shop_fp = 'hungrylion99639807992322'

        root_url = 'https://www.hungrylion.co.za/'

        # 1. Get the main categories
        categories_page = getHTMLSOUPEDDocument(root_url)
        # print(categories_page)
        # List all the categories
        main_categories = categories_page.find_all(
            'figcaption', {'class': 'widget-image-caption wp-caption-text'})

        for i, element in enumerate(main_categories):
            category = str(element.get_text()).strip()

            display_log(Fore.YELLOW, '[{}] {}'.format(i, category))

            if category not in ['DEALS']:
                next_link = 'https://www.hungrylion.co.za/menu-for-one' if category in 'MEALS FOR ONE' else 'https://www.hungrylion.co.za/menu-for-sharing'

                # Open the subcategories page
                subcategories_page = getHTMLSOUPEDDocument(next_link)
                main_subcategories = subcategories_page.find_all('div')

                display_log(
                    Fore.BLUE, '-> subcategories found {}'.format(len(main_subcategories)))
                print('Iterate over all the products')

                # Go through the daily specials
                for j, subcategory in enumerate(main_subcategories):
                    if subcategory.has_attr('data-jltma-wrapper-link'):
                        data_regulator = json.loads(
                            subcategory['data-jltma-wrapper-link'])

                        if data_regulator['is_external'] != 'on':
                            if subcategory.find('figcaption', {'class': 'widget-image-caption wp-caption-text'}) is not None and str(subcategory.find('figcaption', {'class': 'widget-image-caption wp-caption-text'}).get_text()).strip().upper() not in 'DAILY SPECIALS':
                                subcategory_name = str(subcategory.find('figcaption', {
                                                       'class': 'widget-image-caption wp-caption-text'}).get_text()).strip()
                                # Get the next link url
                                products_url = data_regulator['url']

                                # ? Open the products page
                                products_megadata = getHTMLSOUPEDDocument(
                                    products_url)

                                products_parent = products_megadata.find_all('section')[
                                    10].parent

                                # print(data_regulator['url'])
                                # print(subcategory.find('figcaption', {'class':'widget-image-caption wp-caption-text'}))
                                # display_log(Fore.LIGHTMAGENTA_EX, products_parent)
                                # print('--------------------------')
                                # display_log(Fore.LIGHTGREEN_EX, str(products_parent.get_text()).strip()[0])
                                # display_log(Fore.LIGHTYELLOW_EX, products_parent.find('div', {'class':'elementor-row'}))

                                if products_parent is not None and products_parent.find('div', {'class': 'elementor-row'}) is not None:
                                    # products_parent_l1 = products_parent.find('div', {'class':'elementor-row'})
                                    products_parent_l1 = products_parent
                                    # print(products_parent.find_all('div', {'class':'elementor-row'}))

                                    if products_parent_l1 is not None:
                                        # display_log(Fore.LIGHTRED_EX, str(products_parent_l1.get_text()).strip()[0])
                                        products_parent_l2 = products_parent_l1.find_all(
                                            'section', {'class': 'has_ma_el_bg_slider'})
                                        # print(len(products_parent_l2))

                                        # ? Get all the products
                                        for j, product_l3 in enumerate(products_parent_l2):
                                            # Get the products in a row
                                            isolated_products = product_l3.find(
                                                'div', {'class': 'elementor-row'}).find_all('div', {'class': 'has_ma_el_bg_slider'})

                                            for k, product in enumerate(isolated_products):
                                                display_log(
                                                    Fore.LIGHTRED_EX, '[*] {}% - {}'.format(round(i * 100 / len(main_categories)), category))
                                                display_log(
                                                    Fore.CYAN, '{}% - {}'.format(round(j * 100 / len(main_subcategories)), subcategory_name))

                                                product = product.find('div', {
                                                                       'class': 'elementor-widget-wrap'}).find_all('div', {'class': 'elementor-element'})
                                                if len(product) > 0:
                                                    try:
                                                        # Get the name, price and picture
                                                        product_name = str(product[1].find(
                                                            'h4', {'class': 'elementor-heading-title'}).get_text()).strip()
                                                        product_price = str(product[2].find(
                                                            'h4', {'class': 'elementor-heading-title'}).get_text()).strip()
                                                        product_image = str(
                                                            product[0].find('img')['src']).strip()
                                                        product_description = str(product[0].find(
                                                            'p', {'class': 'jltma-image-hover-desc'}).get_text()).strip()

                                                        productId = str(uuid.uuid4())
                                                        sku = str(product_name).upper().replace(' ', '_')

                                                        currency, price = Utility.extract_currency_and_price(product_price)

                                                        # Download the image to the Image Repository
                                                        newProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=product_image, storeId=shop_fp, productId=productId, sku=sku, useProxy=False)

                                                        # Save the model
                                                        # ? SAVE in the db
                                                        # Compile the whole product data model
                                                        TMP_DATA_MODEL = {
                                                            'id': productId,
                                                            'shop_fp': shop_fp,
                                                            'brand': _SHOP_NAME_,
                                                            'product_name': product_name,
                                                            'product_price': str(price),
                                                            'currency': currency,
                                                            'product_picture': [newProductImage],
                                                            'sku': sku,
                                                            'used_link': products_url,
                                                            'category': str(category).upper().strip(),
                                                            'subcategory': str(subcategory_name).upper().strip(),
                                                            'shop_name': _SHOP_NAME_,
                                                            'website_link': root_url,
                                                            'description': product_description,
                                                            'createdAt': int(time.time()) * 1000,
                                                            'updatedAt': int(time.time()) * 1000
                                                        }

                                                        SaveOrUpdateItem.saveOrUpdateItem(TMP_DATA_MODEL=TMP_DATA_MODEL)
                                                        print('----------')
                                                    except Exception as e:
                                                        print(e)
                                                else:
                                                    continue
                                    else:
                                        continue
                                else:
                                    continue

                            else:
                                # display_log(Fore.LIGHTRED_EX, 'Unauthorized subcategory')
                                continue
                        else:
                            continue
                    else:
                        # print('NO data-jltma-wrapper-link FOUND')
                        continue

                    # break
            else:
                # display_log(Fore.LIGHTRED_EX, 'Unauthorized category')
                continue

            # print(next_link[0])
    except Exception as e:
        print(e.with_traceback())


#!Debug
launchBot()
