from pymongo import MongoClient
from django.conf import settings

# Connect using the URI from settings.py
client = MongoClient(settings.MONGO_URI)

# Get the database (ims_db is specified in the URI itself)
db = client.get_database()
