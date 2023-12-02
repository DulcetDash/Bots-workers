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

os.system('clear')

data = Utility.csv_to_json('Dischem - Catalogue - dischem.csv')

shop_fp = 'dischem3092932883788732200043'
_SHOP_NAME_ = 'DIS-CHEM'

imagesStaticReference = Utility.get_filenames_in_directory('Images/')

# print(imagesStaticReference)


def process_product(product):
    product_name = str(product['title']).strip()

    priceString = Utility.removeSpaces(str(product['price']).strip())
    priceString = re.split(r'\s+', priceString)

    if len(priceString) > 1:
        priceString = Utility.removeSpaces(str(priceString[1]).strip())
    else:
        priceString =  Utility.removeSpaces(str(priceString[0]).strip())

    if len(priceString) == 0:
        print('Price not found, item skipped')
        return False

    currency, price = Utility.extract_currency_and_price(priceString)

    root_url = str(product['product href']).strip()

    product_price = str(price)
    product_image = str(product['image-src']).strip()
    imageId = product_image.split('/')
    imageId = imageId[len(imageId)-1]
    imageFetched = Utility.find_image_by_id(image_urls=imagesStaticReference, image_id=imageId)

    print('Image id is {}'.format(imageId))
    print('Found image is {}'.format(imageFetched))

    product_link = str(product['product href']).strip()
    category = 'ALL'
    sku = product_name.upper().replace(' ', '_')

    productId = str(uuid.uuid4())

    # Download the image to the Image Repository
    newProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=product_image, storeId=shop_fp, productId=productId, sku=sku, useProxy=False, directory='Images/', file_name=imageFetched)

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