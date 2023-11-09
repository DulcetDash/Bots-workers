import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load the dataset using pandas
df = pd.read_csv('synthetic_supermarket_products.csv')

# Split the dataset into product descriptions and category labels
product_names = df['ProductName']
categories = df['Category']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(product_names, categories, test_size=0.2, random_state=42)

# Create a pipeline with a TF-IDF vectorizer and an SVM classifier
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english')),
    # Increase the verbosity level to get more info about the training process
    ('classifier', SVC(kernel='linear', verbose=True))
])


print("Starting training...")
pipeline.fit(X_train, y_train)
print("Training completed.")

print("Starting prediction...")
y_pred = pipeline.predict(X_test)
print("Prediction completed.")


# Evaluate the model's performance
print("Classification Report:")
print(classification_report(y_test, y_pred))

# If you want to categorize a new product, you can call the 'predict' method with the trained pipeline
new_product = ['New Product Name']
predicted_category = pipeline.predict(new_product)
print(f"The predicted category for '{new_product[0]}' is '{predicted_category[0]}'")
