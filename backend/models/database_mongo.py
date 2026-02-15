"""
MongoDB Database Implementation
Production-ready database using Motor (async MongoDB driver)
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from motor.motor_asyncio import AsyncIOMotorClient

from utils.logger import get_logger

logger = get_logger(__name__)


class MongoDatabase:
    """MongoDB database implementation"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "mongodb://localhost:27017"
        )
        self.database_name = os.getenv("MONGO_DB_NAME", "marketplace_bot")
        self.client = None
        self.db = None
        self.collection = None
        logger.info(f"MongoDB database configured: {self.database_name}")

    async def initialize(self):
        """Initialize database connection"""
        try:
            self.client = AsyncIOMotorClient(
                self.database_url,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.collection = self.db['item_listings']
            
            # Create indexes
            await self.collection.create_index("id", unique=True)
            await self.collection.create_index("status")
            await self.collection.create_index("created_at")
            await self.collection.create_index([
                ("item_name", "text"),
                ("category", "text"),
                ("brand", "text"),
                ("description", "text")
            ])
            
            logger.info("MongoDB database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MongoDB database: {str(e)}")
            raise

    async def create_listing(self, **kwargs) -> Dict[str, Any]:
        """Create new listing"""
        try:
            # Generate ID if not provided
            if 'id' not in kwargs:
                kwargs['id'] = str(uuid.uuid4())
            
            # Ensure timestamps
            kwargs['created_at'] = kwargs.get('created_at', datetime.now().isoformat())
            kwargs['updated_at'] = datetime.now().isoformat()
            
            # Ensure array fields
            kwargs.setdefault('image_paths', [])
            kwargs.setdefault('marketplace_recommendations', [])
            kwargs.setdefault('posted_to', [])
            
            # Ensure dict fields
            kwargs.setdefault('pricing_data', {})
            kwargs.setdefault('listing_copy', {})
            kwargs.setdefault('analysis_metadata', {})
            kwargs.setdefault('posting_results', {})
            
            # Ensure status
            kwargs.setdefault('status', 'draft')
            
            result = await self.collection.insert_one(kwargs)
            
            if result.inserted_id:
                return await self.get_listing(kwargs['id'])
            else:
                raise Exception("Failed to insert listing")
                
        except Exception as e:
            logger.error(f"Error creating listing: {str(e)}")
            raise

    async def get_listing(self, listing_id: str) -> Optional[Dict[str, Any]]:
        """Get listing by ID"""
        try:
            listing = await self.collection.find_one({"id": listing_id})
            
            if listing:
                # Remove MongoDB's _id field
                listing.pop('_id', None)
                return listing
            return None
                
        except Exception as e:
            logger.error(f"Error getting listing {listing_id}: {str(e)}")
            raise

    async def get_listings(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get listings with optional filtering"""
        try:
            query = {}
            if status:
                query['status'] = status
            
            cursor = self.collection.find(query).sort('created_at', -1).skip(offset).limit(limit)
            listings = await cursor.to_list(length=limit)
            
            # Remove MongoDB's _id field
            for listing in listings:
                listing.pop('_id', None)
            
            return listings
                
        except Exception as e:
            logger.error(f"Error getting listings: {str(e)}")
            raise

    async def update_listing(
        self,
        listing_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update listing"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            result = await self.collection.update_one(
                {"id": listing_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                return await self.get_listing(listing_id)
            return None
                
        except Exception as e:
            logger.error(f"Error updating listing {listing_id}: {str(e)}")
            raise

    async def update_listing_status(
        self,
        listing_id: str,
        posted_to: List[str],
        posting_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update listing posting status"""
        return await self.update_listing(
            listing_id,
            {
                'posted_to': posted_to,
                'posting_results': posting_results,
                'status': 'posted'
            }
        )

    async def delete_listing(self, listing_id: str) -> bool:
        """Delete listing"""
        try:
            result = await self.collection.delete_one({"id": listing_id})
            return result.deleted_count > 0
                
        except Exception as e:
            logger.error(f"Error deleting listing {listing_id}: {str(e)}")
            raise

    async def search_listings(self, query: str) -> List[Dict[str, Any]]:
        """Search listings by query"""
        try:
            # Use text search
            cursor = self.collection.find(
                {"$text": {"$search": query}}
            )
            listings = await cursor.to_list(length=100)
            
            # Remove MongoDB's _id field
            for listing in listings:
                listing.pop('_id', None)
            
            return listings
                
        except Exception as e:
            logger.error(f"Error searching listings: {str(e)}")
            raise

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB database connection closed")
