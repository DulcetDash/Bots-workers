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

data = Utility.csv_to_json('Nov-22-2023.csv')

shop_fp = 'steers83934324341221sas8232980799543533'
_SHOP_NAME_ = 'STEERS'
main_url = 'https://namibia.steers.africa'
initial_product_link = 'https://namibia.steers.africa/menu/steers-burgers'


def process_product(product):
    product_name = str(product['title']).strip()
    product_description = str(product['description']).strip() + ' - ' + str(product['alone_description']).strip()


    priceString =  Utility.removeSpaces(str(product['price']).strip())

    if len(priceString) == 0:
        print('Price not found, item price set to N$0')
        priceString = 'N$0'

    currency, price = Utility.extract_currency_and_price(priceString, divideBy=100)

    print('Currency is {}'.format(currency))

    product_price = str(price)
    currency = currency if len(Utility.removeSpaces(currency).strip()) > 0 else 'N$'

    root_url = str(product['web-scraper-start-url']).strip()
    product_image = main_url + str(product['image-src']).strip()
    product_link = str(product['Pagination-href']).strip()
    product_link = product_link if len(product_link) > 0 else initial_product_link

    category = str(product['alone_description']).strip()
    category = category if len(category) > 0 else 'ALL'

    sku = product_name.upper().replace(' ', '_')

    # Variations
    variations = []

    variation1PriceString = str(product['chips_price']).strip()

    if len(variation1PriceString) > 0:
        _ , priceVariation1 = Utility.extract_currency_and_price(variation1PriceString, divideBy=100)
        variationImage = main_url + str(product['chips_image-src']).strip()
        tmpId = str(uuid.uuid4())
        tmpSku = str(uuid.uuid4())
        newVariationProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=variationImage, storeId=shop_fp, productId=tmpId, sku=tmpSku, useProxy=False)

        variation_1 = {
            'title': str(product['chips_added_title']).strip(),
            'description': '',
            'price': priceVariation1,
            'image': [newVariationProductImage],
            'isPriceTotal': True
        }
        variations.append(variation_1)

    variation2PriceString = str(product['coke_price']).strip()

    if len(variation2PriceString) > 0:
        _ , priceVariation2 = Utility.extract_currency_and_price(variation2PriceString, divideBy=100)
        variationImage = main_url + str(product['coke_image-src']).strip()
        tmpId = str(uuid.uuid4())
        tmpSku = str(uuid.uuid4())
        newVariationProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=variationImage, storeId=shop_fp, productId=tmpId, sku=tmpSku, useProxy=False)

        variation_2 = {
            'title': str(product['coke_added_title']).strip(),
            'description': '',
            'price': priceVariation2,
            'image': [newVariationProductImage],
            'isPriceTotal': True
        }
        variations.append(variation_2)


    productId = str(uuid.uuid4())

    # # Download the image to the Image Repository
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
        'description': product_description,
        'options': variations,
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