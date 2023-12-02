import sys
sys.path.append('../')
import Utility
import SaveOrUpdateItem
import ImageDownloader
import Redis
from pprint import pprint
import datetime
import uuid
import os
import time
import decimal
from concurrent.futures import ThreadPoolExecutor
import asyncio

os.system('clear')

data = Utility.csv_to_json('Shoprite.csv')

shop_fp = 'shoprite8398232980799543533'
_SHOP_NAME_ = 'SHOPRITE'
main_url = 'https://www.shoprite.co.za'


def process_product(product):
    product_name = str(product['title']).strip()

    priceString =  Utility.removeSpaces(str(product['price']).strip())

    if len(priceString) == 0:
        print('Price not found, item skipped')
        return False

    currency, price = Utility.extract_currency_and_price(priceString)

    product_price = str(price)
    root_url = str(product['web-scraper-start-url']).strip()
    product_image = main_url + str(product['image-src']).strip()
    product_link = str(product['pagination-href']).strip()
    category = str(product['categories']).strip().upper()
    sku = product_name.upper().replace(' ', '_')

    productId = str(uuid.uuid4())

    # Download the image to the Image Repository
    newProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=product_image, storeId=shop_fp, productId=productId, sku=sku)

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
    print("Clearing Redis cache")
    Redis.delete_redis_key(shop_fp+'-catalogue')

# Run the main coroutine
asyncio.run(main())