# import ImageResolver
import uuid
from boto3.dynamodb.conditions import Key, Attr
import boto3
from tkinter import Image
from colorama import Back, Fore, Style, init
from decimal import Decimal, ROUND_CEILING
init()


dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-east-1')


def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)

# Save or update items in dynamodb


def saveOrUpdateItem(TMP_DATA_MODEL):
    print('Processing persistence for item: {}'.format(TMP_DATA_MODEL['sku']))
    collection_catalogue = dynamodb.Table('Catalogues')
    collection_store_percentages = dynamodb.Table('PercentagePerStores')
    # ? 1. Check if the item was already catalogued
    ipoItemCatalogued = collection_catalogue.query(
        IndexName='sku-index',
        KeyConditionExpression=Key('sku').eq(TMP_DATA_MODEL['sku']),
        FilterExpression=Attr('shop_fp').eq(TMP_DATA_MODEL['shop_fp'])
    )['Items']

    #! Get the % per stores
    storePercentage = collection_store_percentages.query(
        # IndexName='id',
        KeyConditionExpression=Key('id').eq(TMP_DATA_MODEL['shop_fp'])
    )['Items']

    storePercentage = storePercentage[0]['percentage'] if len(storePercentage) > 0 else 0 #Default to 0%

    TMP_DATA_MODEL['priceAdjusted'] = Decimal(Decimal(TMP_DATA_MODEL['product_price']) + (Decimal(TMP_DATA_MODEL['product_price']) * storePercentage/100)).quantize(Decimal('0.00'), rounding=ROUND_CEILING)
    print('[*] Price adjusted from {} to {}'.format(TMP_DATA_MODEL['product_price'], TMP_DATA_MODEL['priceAdjusted']))
    TMP_DATA_MODEL['currency'] = TMP_DATA_MODEL['currency'].replace(',', '').strip()

    print(ipoItemCatalogued)

    if len(ipoItemCatalogued) > 0:  # ? Item was already catalogued
        ipoItemCatalogued = ipoItemCatalogued[0]
        # ? 2. Prices already updated
        # ? 4. Update the date updated
        TMP_DATA_MODEL.pop('createdAt')
        #! Keep the same id
        TMP_DATA_MODEL['id'] = ipoItemCatalogued['id']

        # ? SAVE
        collection_catalogue.put_item(
            Item=TMP_DATA_MODEL
        )
        display_log(
            Fore.YELLOW, 'Item updated - {}'.format(TMP_DATA_MODEL['sku']))
        print(TMP_DATA_MODEL)

    else:  # ? New item
        display_log(
            Fore.YELLOW, 'New item detected - {}'.format(TMP_DATA_MODEL['sku']))

        collection_catalogue.put_item(
            Item=TMP_DATA_MODEL
        )
        print(TMP_DATA_MODEL)
