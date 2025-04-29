from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid


class MongoBase:
    def __init__(self, collection_name, client=None):
        self.client = client or MongoClient(settings.MONGO_URI)
        self.db = self.client.get_database()
        self.collection = self.db[collection_name]

    @property
    def id(self):
        return str(self._id)    

    def create(self, data):
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating document: {e}")
            return None

    def read(self, item_id):
        try:
            return self.collection.find_one({'_id': ObjectId(item_id)})
        except Exception as e:
            print(f"Error reading document: {e}")
            return None

    def update(self, item_id, data):
        try:
            self.collection.update_one({'_id': ObjectId(item_id)}, {'$set': data})
            return self.read(item_id)
        except Exception as e:
            print(f"Error updating document: {e}")
            return None

    def delete(self, item_id):
        try:
            self.collection.delete_one({'_id': ObjectId(item_id)})
        except Exception as e:
            print(f"Error deleting document: {e}")
            return None

    def all(self):
        try:
            return [self.add_item_id(item) for item in self.collection.find()]
        except Exception as e:
            print(f"Error fetching all documents: {e}")
            return []

    def search(self, field, query):
        try:
            return [self.add_item_id(item) for item in self.collection.find({field: {'$regex': query, '$options': 'i'}})]
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def add_item_id(self, item):
        """Add 'item_id' field to the item, accessible safely in templates."""
        item['item_id'] = str(item.get('_id'))  # Convert ObjectId to string for easy access
        return item


class Product(MongoBase):
    def __init__(self, client=None):
        super().__init__('products', client)

    def create(self, data, image_file=None):
        if image_file:
            image_url = self.save_image(image_file)
            data['image_url'] = image_url  # Save image URL in MongoDB
        return super().create(data)

    def save_image(self, image_file):
        file_name = os.path.join('product_images', str(uuid.uuid4()) + os.path.splitext(image_file.name)[1])
        file_path = default_storage.save(file_name, ContentFile(image_file.read()))
        file_url = default_storage.url(file_path)
        return file_url

    def delete_image(self, image_url):
        try:
            file_path = image_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting image: {e}")


class Category(MongoBase):
    def __init__(self, client=None):
        super().__init__('categories', client)


class Customer(MongoBase):
    def __init__(self, client=None):
        super().__init__('customers', client)


class Supplier(MongoBase):
    def __init__(self, client=None):
        super().__init__('suppliers', client)
