import csv
import json
import re
import os

def csv_to_json(csv_file_path):
    # Create an empty list to store the CSV rows as dictionaries
    data_list = []
    
    # Open the CSV file for reading
    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        # Use csv.DictReader to read the CSV file into a dictionary
        csv_reader = csv.DictReader(csvfile)
        
        # Loop over the CSV rows
        for row in csv_reader:
            # Append each row to the data list
            data_list.append(row)
    
    # Convert the list of dictionaries into a JSON string and then parse it into a Python object
    json_object = json.loads(json.dumps(data_list))
    
    return json_object


def extract_currency_and_price(price_string, returnString=True, divideBy=1, fallbackCurrency='N$'):
    price_string = removeSpaces(price_string)
    # Initialize variables to hold the extracted currency symbol and the price
    currency_symbol = ''
    price = ''

    # Iterate through each character in the string
    for char in price_string:
        # If the character is a digit or a decimal point, add it to the price
        if char.isdigit() or char == '.':
            price += char
        # Otherwise, if it's not a space, it should be part of the currency symbol
        elif not char.isspace():
            currency_symbol += char

    price = 0 if len(price)<=0 else price

    divideBy = divideBy if divideBy > 0 else 1

    # Convert the extracted price to a float
    price_value = float(str(price).replace(',', '')) / divideBy

    price_value = str(price_value) if returnString else price_value

    if len(currency_symbol.strip())<=0:
        currency_symbol = fallbackCurrency

    return currency_symbol, price_value

def removeSpaces(string):
    return re.sub(r'\s+', '', string)


def extract_image_sources(html):
    # Regular expression to match all <img> tags and extract src
    pattern = r'<img[^>]+src="([^">]+)"'
    # Find all instances of the pattern
    urls = re.findall(pattern, html)
    return urls


def find_image_by_id(image_urls, image_id):
    for url in image_urls:
        if image_id in url:
            return url
    return 'placeholder'


def extract_id_image_dict(content):
    # General regex pattern to match all image URLs
    general_url_pattern = r'https?://[^\s]+?\.(?:png|jpg|jpeg|svg|gif)(?:\?[^"\s]+)?'
    
    # Specific pattern for extracting ID from 'cdn.tictuk.com' URLs
    specific_id_pattern = r'https://cdn\.tictuk\.com/[^/]+/[^/]+/([a-f0-9-]+)\.[a-z]+'

    all_urls = re.findall(general_url_pattern, content)

    # Constructing the dictionary
    id_image_dict = {}
    for url in all_urls:
        specific_match = re.search(specific_id_pattern, url)
        if specific_match:
            # If it's a 'cdn.tictuk.com' URL, extract the ID
            id_image_dict[specific_match.group(1)] = url
        else:
            # Otherwise, use the entire URL as the key
            id_image_dict[url] = url

    return id_image_dict


def get_filenames_in_directory(directory):
    """
    This function takes a directory path and returns an array of filenames in that directory.
    """
    # List all files in the directory
    filenames = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return filenames