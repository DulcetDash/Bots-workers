from threading import local
import requests
import uuid
import validators
import boto3
import requests
from io import BytesIO


def downloadImage(name, url):
    try:
        img_data = requests.get(url).content
        with open('/Users/dominiquekanyik/Documents/Work/Group/Delivery/Bots-workers/Catalogue_images/{}'.format(name), 'wb') as handler:
            handler.write(img_data)
            return True
    except:
        return False


# Initialize a session using Amazon S3
s3 = boto3.client('s3',
                  aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                  aws_secret_access_key='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',
                  region_name='us-east-1',
                  )


def upload_image_to_s3(name, url, bucket_name):
    try:
        # Get image content from the URL
        img_data = requests.get(url).content
        img_byte_stream = BytesIO(img_data)

        # Upload the file
        s3.upload_fileobj(img_byte_stream, bucket_name, name,
                          ExtraArgs={'ContentType': 'image/jpeg'}
                          )
        print(f"Image {name} uploaded to {bucket_name}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Generate or update the image registry


def updateImageregistry(TMP_DATA_MODEL):
    try:
        local_images_registry = {}
        try:
            local_images_registry = TMP_DATA_MODEL['local_images_registry']
        except:
            local_images_registry = {}
        # ...
        images_array = TMP_DATA_MODEL['product_picture']
        clean_original_pictures = []  # Will keep the list of all the clean and valid images

        # Auto generate registry entries based on if the image was downloaded
        for image_link in images_array:
            #! Check if the link is valid
            if validators.url(image_link):
                # ? Save the clean link
                clean_original_pictures.append(image_link)

                if image_link not in local_images_registry:  # ! Not yet registered - update
                    try:
                        tmp_name = '{}-{}.jpg'.format(
                            str(uuid.uuid4()), TMP_DATA_MODEL['shop_fp']).lower().replace('-', '_').strip()

                        if upload_image_to_s3(tmp_name, image_link, 'products-images-dd'):
                            # Update the local registry
                            print('Saving the registry entry for -> {}'.format(tmp_name))
                            local_images_registry[image_link] = tmp_name
                    except:
                        print('Error while uploading the image')
                        continue
                else:  # ! Already registered - ignore
                    print('Already registered, skipping')
                    continue

        # print(local_images_registry)
        # ? Update the original images
        TMP_DATA_MODEL['product_picture'] = clean_original_pictures
        # ? Update the data model
        TMP_DATA_MODEL['local_images_registry'] = local_images_registry

        return TMP_DATA_MODEL
    except:
        return TMP_DATA_MODEL
