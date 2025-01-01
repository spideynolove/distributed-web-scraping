from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Dict, List, Optional
import logging
from datetime import datetime

class MongoStorage:
    """MongoDB storage implementation for scraped data"""
    
    def __init__(self, connection_string: str, database_name: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.logger = logging.getLogger(__name__)
        
        # Collection names
        self.collections = {
            'products': 'ecommerce_products',
            'financial_data': 'financial_records',
            'logs': 'scraping_logs'
        }

    def insert_data(self, collection_name: str, data: Dict) -> bool:
        """Insert a single document into the specified collection"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection name: {collection_name}")
                
            collection = self.db[self.collections[collection_name]]
            data['created_at'] = datetime.utcnow()
            result = collection.insert_one(data)
            return result.acknowledged
        except PyMongoError as e:
            self.logger.error(f"Error inserting data: {e}")
            return False

    def bulk_insert(self, collection_name: str, data: List[Dict]) -> bool:
        """Insert multiple documents into the specified collection"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection name: {collection_name}")
                
            collection = self.db[self.collections[collection_name]]
            for item in data:
                item['created_at'] = datetime.utcnow()
            result = collection.insert_many(data)
            return result.acknowledged
        except PyMongoError as e:
            self.logger.error(f"Error in bulk insert: {e}")
            return False

    def update_data(self, collection_name: str, query: Dict, update: Dict) -> bool:
        """Update documents matching the query"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection name: {collection_name}")
                
            collection = self.db[self.collections[collection_name]]
            update['$set']['updated_at'] = datetime.utcnow()
            result = collection.update_many(query, update)
            return result.acknowledged
        except PyMongoError as e:
            self.logger.error(f"Error updating data: {e}")
            return False

    def find_data(self, collection_name: str, query: Dict, limit: int = 100) -> List[Dict]:
        """Find documents matching the query"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection name: {collection_name}")
                
            collection = self.db[self.collections[collection_name]]
            return list(collection.find(query).limit(limit))
        except PyMongoError as e:
            self.logger.error(f"Error finding data: {e}")
            return []

    def get_collection_stats(self, collection_name: str) -> Optional[Dict]:
        """Get statistics about a collection"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Invalid collection name: {collection_name}")
                
            collection = self.db[self.collections[collection_name]]
            return collection.aggregate([
                {
                    '$group': {
                        '_id': None,
                        'count': {'$sum': 1},
                        'first_insert': {'$min': '$created_at'},
                        'last_insert': {'$max': '$created_at'}
                    }
                }
            ]).next()
        except (PyMongoError, StopIteration) as e:
            self.logger.error(f"Error getting collection stats: {e}")
            return None

    def close(self):
        """Close the MongoDB connection"""
        self.client.close()