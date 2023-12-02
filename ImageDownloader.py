import boto3
import requests
import mimetypes
import uuid
from io import BytesIO
from boto3.dynamodb.conditions import Key, Attr
import re
import os

s3_bucket = 'products-images-catalogue-dd'
dynamodb_table = 'ImageRepository'

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-east-1')
table = dynamodb.Table(dynamodb_table)
collection_catalogue = dynamodb.Table('Catalogues')



def upload_image_to_s3_and_save_to_dynamodb(image_url, storeId, productId, sku, useProxy=True,directory=None, file_name=None):
    proxy_config = {
        "http": "http://splgc8k729:tuwGvtk6n2b78LPgEy@gate.smartproxy.com:7000",
        "https": "https://splgc8k729:tuwGvtk6n2b78LPgEy@gate.smartproxy.com:7000"
    }

    try:
        # ? 1. Check if the item was already catalogued
        ipoItemCatalogued = collection_catalogue.query(
            IndexName='sku-index',
            KeyConditionExpression=Key('sku').eq(sku),
            FilterExpression=Attr('shop_fp').eq(storeId)
        )['Items']

        if len(ipoItemCatalogued) > 0:  # ? Item was already catalogued
            productId = ipoItemCatalogued[0]['id']


        # Check if a record already exists
        print(f"Checking if record exists for storeId={storeId} and productId={productId}")
        response = table.query(
            IndexName='storeId-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('storeId').eq(storeId),
            FilterExpression=boto3.dynamodb.conditions.Attr('active').eq(True)
        )

        pattern = r"\.svg"
        matchUnrelatedImage = re.search(pattern, ipoItemCatalogued[0]['product_picture'][0] if len(ipoItemCatalogued) > 0 else '', re.IGNORECASE)

        print(f"matchUnrelatedImage: {matchUnrelatedImage}")

        # Check for existing active records with the same productId
        existing_record = next((item for item in response.get('Items', []) if item['productId'] == productId), None)
        if existing_record and matchUnrelatedImage is None:
            print("Active record found, returning existing s3Uri")
            return existing_record['s3Uri']
        
        #Check if a record exists with the image url from dynamo
        imageInRepo = table.query(
            IndexName='originalImageurl-index',
            KeyConditionExpression=Key('originalImageUrl').eq(image_url),
            FilterExpression=Attr('storeId').eq(storeId)
        )['Items']

        if len(imageInRepo) > 0:
            print("Image already exists in the repo")
            # Update the existing record's productId and active status
            print(f"Updating existing record for storeId={storeId} and productId={productId}")
            table.update_item(
                Key={'id': imageInRepo[0]['id']},
                UpdateExpression='SET productId = :productId, active = :active',
                ExpressionAttributeValues={
                    ':productId': productId,
                    ':active': True
                }
            )
            return imageInRepo[0]['s3Uri']

        # Download the image
        if directory == None and file_name == None:
            print(f"Downloading {image_url}")
            response = None

            # ? Wasn't predownloaded
            if useProxy:
                response = requests.get(image_url, proxies=proxy_config, stream=True)
            else:
                response = requests.get(image_url, stream=True)

            if response.status_code != 200:
                print(f"Error: Status code {response.status_code}")
                return image_url

            # Get the content type and calculate the file extension
            content_type = response.headers.get('content-type')
            extension = mimetypes.guess_extension(content_type) or '.jpg'
            filename = f'{storeId}/{productId}/image{extension}'

            # Upload the image to S3
            print(f"Uploading to s3://{s3_bucket}/{filename}")
            s3_client.upload_fileobj(
                BytesIO(response.content),
                s3_bucket,
                filename,
                ExtraArgs={'ContentType': content_type}
            )
            s3_uri = f's3://{s3_bucket}/{filename}'

            # If no active record exists, save a new detail in DynamoDB
            print(f"Saving new detail for productId={productId}")
            imageId = str(uuid.uuid4())
            table.put_item(
                Item={
                    'id': imageId,
                    'storeId': storeId,
                    'productId': productId,
                    'originalImageUrl': image_url,
                    's3Uri': s3_uri,
                    'active': True
                }
            )
            return s3_uri
        else:
            if file_name=='placeholder':
                return 's3://products-images-catalogue-dd/placeholder.png'

            print('Local image detected')
            # Full path to the file
            file_path = os.path.join(directory, file_name)

            print('Filepath: {}'.format(file_path))

            extension = str(file_name).split('.')
            extension = extension[len(extension)-1]

            # Key for the object in S3 (can be different from the file name)
            filename = f'{storeId}/{productId}/image.{extension}'

            try:
                # Upload the file
                s3_client.upload_file(file_path, s3_bucket, filename)

                # Construct the URI
                image_url = f's3://{s3_bucket}/{filename}'

                # Was predownloaded - just record in the repo
                print(f"Saving new detail for productId={productId}")
                imageId = str(uuid.uuid4())
                table.put_item(
                    Item={
                        'id': imageId,
                        'storeId': storeId,
                        'productId': productId,
                        'originalImageUrl': file_name,
                        's3Uri': image_url,
                        'active': True
                    }
                )
                return image_url
            except Exception as e:
                return 's3://products-images-catalogue-dd/placeholder.png'

    except Exception as e:
        print(f"An error occurred: {e}")
        return image_url

# Example usage

# productId = 'abcwd'
# image_url = "https://www.dischem.co.za/media/catalog/product/cache/c4abad14a8c43409b019ba95c1f3e4f0/1/5/159693_1_1.jpg"
# storeId = '123456'
# upload_image_to_s3_and_save_to_dynamodb(image_url, storeId, productId, 'test')
