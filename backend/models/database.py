"""
Database Models and Management
Simple JSON-based database for development (can be replaced with PostgreSQL/MongoDB)
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from pathlib import Path


class ItemListing:
    """Item listing model"""

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.item_name = kwargs.get('item_name')
        self.category = kwargs.get('category')
        self.brand = kwargs.get('brand')
        self.condition = kwargs.get('condition')
        self.description = kwargs.get('description')
        self.image_paths = kwargs.get('image_paths', [])
        self.pricing_data = kwargs.get('pricing_data', {})
        self.marketplace_recommendations = kwargs.get('marketplace_recommendations', [])
        self.listing_copy = kwargs.get('listing_copy', {})
        self.analysis_metadata = kwargs.get('analysis_metadata', {})
        self.status = kwargs.get('status', 'draft')  # draft, posted, sold, archived
        self.posted_to = kwargs.get('posted_to', [])
        self.posting_results = kwargs.get('posting_results', {})
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'item_name': self.item_name,
            'category': self.category,
            'brand': self.brand,
            'condition': self.condition,
            'description': self.description,
            'image_paths': self.image_paths,
            'pricing_data': self.pricing_data,
            'marketplace_recommendations': self.marketplace_recommendations,
            'listing_copy': self.listing_copy,
            'analysis_metadata': self.analysis_metadata,
            'status': self.status,
            'posted_to': self.posted_to,
            'posting_results': self.posting_results,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemListing':
        """Create from dictionary"""
        return cls(**data)


class Database:
    """Simple JSON-based database (replace with real DB in production)"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "listings.json"
        )
        self.listings: Dict[str, ItemListing] = {}

    async def initialize(self):
        """Initialize database"""
        # Create data directory if it doesn't exist
        Path(os.path.dirname(self.db_path)).mkdir(parents=True, exist_ok=True)

        # Load existing data if available
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.listings = {
                        k: ItemListing.from_dict(v)
                        for k, v in data.items()
                    }
                print(f"Loaded {len(self.listings)} listings from database")
            except Exception as e:
                print(f"Error loading database: {str(e)}")
                self.listings = {}
        else:
            print("Initialized new database")

    async def save(self):
        """Save database to disk"""
        try:
            data = {
                k: v.to_dict()
                for k, v in self.listings.items()
            }

            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving database: {str(e)}")

    async def create_listing(self, **kwargs) -> ItemListing:
        """Create new listing"""
        listing = ItemListing(**kwargs)
        self.listings[listing.id] = listing
        await self.save()
        return listing

    async def get_listing(self, listing_id: str) -> Optional[ItemListing]:
        """Get listing by ID"""
        return self.listings.get(listing_id)

    async def get_listings(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get listings with optional filtering"""
        listings = list(self.listings.values())

        # Filter by status if provided
        if status:
            listings = [l for l in listings if l.status == status]

        # Sort by created date (newest first)
        listings.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        listings = listings[offset:offset + limit]

        return [l.to_dict() for l in listings]

    async def update_listing(
        self,
        listing_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ItemListing]:
        """Update listing"""
        listing = self.listings.get(listing_id)
        if not listing:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(listing, key):
                setattr(listing, key, value)

        listing.updated_at = datetime.now().isoformat()

        await self.save()
        return listing

    async def update_listing_status(
        self,
        listing_id: str,
        posted_to: List[str],
        posting_results: Dict[str, Any]
    ) -> Optional[ItemListing]:
        """Update listing posting status"""
        listing = self.listings.get(listing_id)
        if not listing:
            return None

        listing.posted_to = posted_to
        listing.posting_results = posting_results
        listing.status = 'posted'
        listing.updated_at = datetime.now().isoformat()

        await self.save()
        return listing

    async def delete_listing(self, listing_id: str) -> bool:
        """Delete listing"""
        if listing_id in self.listings:
            del self.listings[listing_id]
            await self.save()
            return True
        return False

    async def search_listings(self, query: str) -> List[Dict[str, Any]]:
        """Search listings by query"""
        query_lower = query.lower()
        results = []

        for listing in self.listings.values():
            # Search in item name, category, brand, description
            if (
                query_lower in listing.item_name.lower() or
                query_lower in listing.category.lower() or
                (listing.brand and query_lower in listing.brand.lower()) or
                query_lower in listing.description.lower()
            ):
                results.append(listing.to_dict())

        return results
