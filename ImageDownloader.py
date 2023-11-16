import boto3
import requests
import mimetypes
import uuid
from io import BytesIO
from boto3.dynamodb.conditions import Key, Attr

def upload_image_to_s3_and_save_to_dynamodb(image_url, storeId, productId, sku):
    s3_bucket = 'products-images-catalogue-dd'
    dynamodb_table = 'ImageRepository'

    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-east-1')
    table = dynamodb.Table(dynamodb_table)

    proxy_config = {
        "http": "http://splgc8k729:tuwGvtk6n2b78LPgEy@gate.smartproxy.com:7000",
        "https": "https://splgc8k729:tuwGvtk6n2b78LPgEy@gate.smartproxy.com:7000"
    }

    try:
        collection_catalogue = dynamodb.Table('Catalogues')
        # ? 1. Check if the item was already catalogued
        ipoItemCatalogued = collection_catalogue.query(
            IndexName='sku-index',
            KeyConditionExpression=Key('sku').eq(sku),
            FilterExpression=Attr('shop_fp').eq(storeId)
        )['Items']

        if len(ipoItemCatalogued) > 0:  # ? Item was already catalogued
            ipoItemCatalogued = ipoItemCatalogued[0]
            productId = ipoItemCatalogued['id']


        # Check if a record already exists
        print(f"Checking if record exists for storeId={storeId} and productId={productId}")
        response = table.query(
            IndexName='storeId-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('storeId').eq(storeId),
            FilterExpression=boto3.dynamodb.conditions.Attr('active').eq(True)
        )

        # Check for existing active records with the same productId
        existing_record = next((item for item in response.get('Items', []) if item['productId'] == productId), None)
        if existing_record:
            print("Active record found, returning existing s3Uri")
            return existing_record['s3Uri']

        # Download the image
        print(f"Downloading {image_url}")
        response = requests.get(image_url, proxies=proxy_config, stream=True)
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
    except Exception as e:
        print(f"An error occurred: {e}")
        return image_url

# Example usage

# productId = 'abcwd'
# image_url = "https://www.dischem.co.za/media/catalog/product/cache/c4abad14a8c43409b019ba95c1f3e4f0/1/5/159693_1_1.jpg"
# storeId = '123456'
# upload_image_to_s3_and_save_to_dynamodb(image_url, storeId, productId, 'test')
