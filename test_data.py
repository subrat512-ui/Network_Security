from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import os

load_dotenv()

uri = os.getenv("MONGO_DB_URI")

print("=" * 60)
print("URI:", uri)

client = MongoClient(uri)

# Show all databases
print("\nDatabases:")
print(client.list_database_names())

# Select database
db = client["Manan"]

# Show collections
print("\nCollections:")
print(db.list_collection_names())

# Select collection
collection = db["network_security"]

# Count documents
count = collection.count_documents({})
print("\nDocument Count:", count)

# First document
doc = collection.find_one()
print("\nFirst Document:")
print(doc)

# Convert to DataFrame
df = pd.DataFrame(list(collection.find()))

print("\nDataFrame Shape:", df.shape)
print(df.head())

if "_id" in df.columns:
    df.drop(columns="_id", inplace=True)

print("\nAfter dropping _id:")
print(df.shape)
print(df.head())