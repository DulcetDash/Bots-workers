from tkinter import Image
from colorama import Back, Fore, Style, init
init()
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid

import ImageResolver

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)

# Save or update items in dynamodb
def saveOrUpdateItem(TMP_DATA_MODEL):
    collection_catalogue = dynamodb.Table('catalogue_central')
    #? 1. Check if the item was already catalogued
    ipoItemCatalogued = collection_catalogue.query(
        IndexName='sku-index',
        KeyConditionExpression=Key('sku').eq(TMP_DATA_MODEL['sku']),
        FilterExpression=Attr('product_name').eq(TMP_DATA_MODEL['product_name'])
    )['Items']

                            
    if len(ipoItemCatalogued)>0:    #? Item was already catalogued
        ipoItemCatalogued = ipoItemCatalogued[0]
        #? 2. Prices already updated
        #? 3. Merge and unify the product pictures
        #! Fix incorrect [[image_link]] format to [image_link]
        TMP_DATA_MODEL['product_picture'] = [] if len(TMP_DATA_MODEL['product_picture'])<=0 else TMP_DATA_MODEL['product_picture'] if isinstance(TMP_DATA_MODEL['product_picture'][0], str) else TMP_DATA_MODEL['product_picture'][0]
        #!---
        TMP_DATA_MODEL['product_picture'] += ipoItemCatalogued['product_picture']
        TMP_DATA_MODEL['product_picture'] = list(dict.fromkeys(TMP_DATA_MODEL['product_picture']))
        #? 4. Update the date updated
        TMP_DATA_MODEL['date_updated'] = TMP_DATA_MODEL['date_added']
        TMP_DATA_MODEL['date_added'] = ipoItemCatalogued['date_added']
        #! Keep the same _id
        TMP_DATA_MODEL['_id'] = ipoItemCatalogued['_id']
        #! Keep the local registry image
        try:
            TMP_DATA_MODEL['local_images_registry'] = ipoItemCatalogued['local_images_registry']
        except:
            TMP_DATA_MODEL['local_images_registry'] = {}

        #? Resolve the images situation
        TMP_DATA_MODEL = ImageResolver.updateImageregistry(TMP_DATA_MODEL=TMP_DATA_MODEL)

        #? SAVE
        collection_catalogue.put_item(
            Item=TMP_DATA_MODEL
        )
        display_log(Fore.YELLOW,'Item updated - {}'.format(TMP_DATA_MODEL['sku']))
        print(TMP_DATA_MODEL)
                            

    else:   #? New item
        display_log(Fore.YELLOW,'New item detected - {}'.format(TMP_DATA_MODEL['sku']))

        TMP_DATA_MODEL['local_images_registry'] = {}

        #? Resolve the images situation
        TMP_DATA_MODEL = ImageResolver.updateImageregistry(TMP_DATA_MODEL=TMP_DATA_MODEL)
        
        collection_catalogue.put_item(
            Item=TMP_DATA_MODEL
        )
        print(TMP_DATA_MODEL)