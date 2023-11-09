import sys
sys.path.append('../')
import Utility
import SaveOrUpdateItem
from pprint import pprint
import datetime
import uuid
import os
import time
import decimal
import re
from concurrent.futures import ThreadPoolExecutor
import asyncio

os.system('clear')

data = Utility.csv_to_json('Catalogue-Nov-9-2023.csv')

shop_fp = 'picknpay8837887322322'
_SHOP_NAME_ = 'PICK N PAY'

def process_product(product):
    product_name = str(product['title']).strip()

    priceString = str(product['price']).strip()
    priceString = re.split(r'\s+', priceString)

    if len(priceString) > 1:
        priceString = Utility.removeSpaces(str(priceString[1]).strip())
    else:
        priceString =  Utility.removeSpaces(str(priceString[0]).strip())

    if len(priceString) == 0:
        print('Price not found, item skipped')
        return False

    currency, price = Utility.extract_currency_and_price(priceString)

    root_url = str(product['web-scraper-start-url']).strip()

    product_price = str(price)
    product_image = str(product['image-src']).strip()
    product_link = str(product['pagination-href']).strip()
    category = root_url.split('/')
    category = category[len(category) - 1].upper().replace('-', ' ').replace(' 423144840', '').upper()
    sku = product_name.upper().replace(' ', '_')

    TMP_DATA_MODEL = {
        'id': str(uuid.uuid4()),
        'shop_fp': shop_fp,
        'brand': _SHOP_NAME_,
        'product_name': product_name,
        'product_price': product_price,
        'currency': currency,
        'product_picture': [product_image],
        'sku': sku,
        'used_link': product_link,
        'category': category,
        'subcategory': category,
        'shop_name': _SHOP_NAME_,
        'website_link': root_url,
        'description': '',
        'createdAt': int(time.time()) * 1000,
        'updatedAt': int(time.time()) * 1000
    }

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

# Run the main coroutine
asyncio.run(main())
