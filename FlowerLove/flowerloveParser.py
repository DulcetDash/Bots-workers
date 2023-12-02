import sys
sys.path.append('../')
import Utility
import SaveOrUpdateItem
import ImageDownloader
from pprint import pprint
import datetime
import uuid
import os
import time
import decimal
import re
from concurrent.futures import ThreadPoolExecutor
import asyncio
import Redis
import json

os.system('clear')

data = Utility.csv_to_json('Nov-25-2023.csv')

shop_fp = 'flowerlove932032932883788732203283i7843'
_SHOP_NAME_ = 'FLOWER LOVE FLORIST'


def getSpecifiRosesPrices(dataValue, refinedOptions, title='COLOR'):
    tmp = str(dataValue).replace('Please choose0', '').replace('(', '').replace('\xa0', '').replace('+', '').replace('Roses ','').split(')')
    tmp = tmp[:len(tmp)-1]

    for el in tmp:
        tmpPrice = el.split(' ')
        _, price = Utility.extract_currency_and_price(tmpPrice[1])
        refinedOptions.append({
            'title': '{} {} roses'.format(tmpPrice[0], title),
            'price': price,
            'isPriceTotal': False
        })
    return refinedOptions



def parse_flower_string(data):
    if not data:
        return []
    # Convert the data to a list of dictionaries
    data_list = json.loads(data)

    if len(data_list) <= 0:
        return []

    refinedOptions = []

    #Segregate the data
    for options in data_list:
        dataLabel = options['custom roses number-aria-label']
        dataValue = options['custom roses number']

        if dataLabel=='Vase':
            tmp = str(dataValue).split(' ')
            tmpPrice = str(tmp[len(tmp)-1]).replace('(', '').replace(')','').replace('+', '')
            _, price = Utility.extract_currency_and_price(tmpPrice)

            refinedOptions.append({
                'title': 'Add a Vase',
                'price': price,
                'isPriceTotal': False
            })

        elif dataLabel=='Customize Amount of Roses' or dataLabel=='How Many Roses':
            tmp = str(dataValue).replace('Please choose', '').replace('(', '').replace('\xa0', '').replace('+', '').replace('Roses ','').split(')')
            tmp = tmp[:len(tmp)-1]

            for el in tmp:
                tmpPrice = el.split(' ')
                _, price = Utility.extract_currency_and_price(tmpPrice[1])
                refinedOptions.append({
                    'title': '{} roses'.format(tmpPrice[0]),
                    'price': price,
                    'isPriceTotal': False
                })
        elif dataLabel=='White Roses':
            refinedOptions = getSpecifiRosesPrices(dataValue, refinedOptions, 'White')
        elif dataLabel=='Pink Roses':
            refinedOptions = getSpecifiRosesPrices(dataValue, refinedOptions, 'Pink')
        elif dataLabel=='Orange Roses':
            refinedOptions = getSpecifiRosesPrices(dataValue, refinedOptions, 'Orange')
        elif dataLabel=='Red Roses':
            refinedOptions = getSpecifiRosesPrices(dataValue, refinedOptions, 'Red')
        else:
            print('Unknown data found? {}'.format(options))
    

    return refinedOptions
        


def process_product(product):
    product_name = str(product['title']).strip()
    description = str(product['description'])

    priceString = Utility.removeSpaces(str(product['price']).strip())

    currency, price = Utility.extract_currency_and_price(priceString)

    root_url = 'https://www.flowerloveflorist.com'

    product_price = str(price)
    product_image = str(product['image-src']).strip()

    product_link = str(product['Links-href']).strip()
    category = 'ALL'
    sku = product_name.upper().replace(' ', '_')

    # Variations
    variations = parse_flower_string(product['custom roses number'])

    productId = str(uuid.uuid4())

    # Download the image to the Image Repository
    newProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=product_image, storeId=shop_fp, productId=productId, sku=sku, useProxy=False)

    TMP_DATA_MODEL = {
        'id': productId,
        'shop_fp': shop_fp,
        'brand': _SHOP_NAME_,
        'product_name': product_name,
        'product_price': product_price,
        'currency': currency,
        'product_picture': [newProductImage],
        'sku': sku,
        'used_link': product_link,
        'category': category,
        'subcategory': category,
        'shop_name': _SHOP_NAME_,
        'website_link': root_url,
        'description': description,
        'options': variations,
        'createdAt': int(time.time()) * 1000,
        'updatedAt': int(time.time()) * 1000
    }

    print(TMP_DATA_MODEL)

    SaveOrUpdateItem.saveOrUpdateItem(TMP_DATA_MODEL=TMP_DATA_MODEL)
    print(70*'-')
    return True


# This is an async wrapper for your synchronous function
async def async_task(index,product):
    index+=1
    print(f"[{index}] Processing product {product['title']}")
    loop = asyncio.get_running_loop()
    # Run the synchronous function in the ThreadPoolExecutor
    result = await loop.run_in_executor(None, process_product, product)
    return result


async def main():
    index = 0
    tasks = [async_task(index, product) for product in data]
    
    # asyncio.gather waits for all the tasks to complete
    results = await asyncio.gather(*tasks)
    print(f"All tasks returned: {len(results)}")
    print("Clearing Redis cache")
    Redis.delete_redis_key(shop_fp+'-catalogue')

# Run the main coroutine
asyncio.run(main())