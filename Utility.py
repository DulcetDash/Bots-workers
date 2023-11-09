import csv
import json
import re

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


def extract_currency_and_price(price_string):
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

    # Convert the extracted price to a float
    price_value = float(str(price).replace(',', ''))

    return currency_symbol, price_value

def removeSpaces(string):
    return re.sub(r'\s+', '', string)