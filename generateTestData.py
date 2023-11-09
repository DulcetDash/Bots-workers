import pandas as pd
import random

# Define some generic categories
categories = [
    'Bakery', 'Beverages', 'Produce', 'Snacks', 'Dairy',
    'Meat', 'Seafood', 'Frozen Foods', 'Delicatessen', 'Household'
]

# Function to generate a random product name
def generate_product_name():
    nouns = ['Bread', 'Milk', 'Lettuce', 'Chips', 'Cheese', 'Chicken', 'Shrimp', 'Ice Cream', 'Ham', 'Detergent']
    adjectives = ['Fresh', 'Organic', 'Frozen', 'Crunchy', 'Natural', 'Grilled', 'Marinated', 'Creamy', 'Smoked', 'Eco']
    return random.choice(adjectives) + " " + random.choice(nouns)

# Generate the dataset
data = {
    'ProductName': [generate_product_name() for _ in range(100000)],
    'Category': [random.choice(categories) for _ in range(100000)]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('synthetic_supermarket_products.csv', index=False)

print("Synthetic supermarket products dataset generated and saved to 'synthetic_supermarket_products.csv'.")
