import cv2
import numpy as np
import requests
from duckduckgo_images_api import search
import logging
import boto3

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

for name in logging.Logger.manager.loggerDict.keys():
    if ('boto' in name) or ('urllib3' in name):
        logging.getLogger(name).setLevel(logging.WARNING)

# Set up logging
# logging.basicConfig()
# logging.getLogger('botocore').setLevel(logging.ERROR)
# logging.getLogger('boto3').setLevel(logging.CRITICAL)

# Initialize a DynamoDB resource using boto3
dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-east-1')
table = dynamodb.Table('Catalogues')
client = boto3.client('dynamodb')

# Define a threshold for what you consider to be a blurry image
BLUR_THRESHOLD = 100.0

def is_blurry(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    return fm < BLUR_THRESHOLD

def download_image(image_url):
    try:
        response = requests.get(image_url, timeout=5)  # 5 seconds timeout
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        image_data = response.content
        image = np.asarray(bytearray(image_data), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        # print(f"Failed to download or an error occurred for {image_url}. Error: {e}")
        return None

def fetch_image_urls():
    # Implement this function to fetch image URLs from DynamoDB
    # For example:
    response = table.scan()
    return {item['id']: {'url': item['product_picture'][0], 'name': item['product_name']} for item in response['Items']}  # Adjust keys as per your table's schema

def searchBetterImage(image_name):
    print(image_name)
    results = search(image_name)
    print(results)

def check_images():
    image_urls = fetch_image_urls()

    for image_key, imageObj in image_urls.items():
        image_url = imageObj['url']
        image_name = imageObj['name']

        image = download_image(image_url)
        if image is None:
            print(f"[{image_key}] Image at {image_url} is inaccessible.")
            print(50*'-')
            searchBetterImage(image_name=image_name)
            continue

        if is_blurry(image):
            print(f"[{image_key}] Image at {image_url} is blurry.")
            print(50*'-')
            continue
        # break

if __name__ == "__main__":
    check_images()
