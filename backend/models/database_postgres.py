"""
PostgreSQL Database Implementation
Production-ready database using SQLAlchemy and PostgreSQL
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select
from sqlalchemy import update, delete
import json

from utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class ItemListingModel(Base):
    """SQLAlchemy model for item listings"""
    __tablename__ = 'item_listings'

    id = Column(String, primary_key=True)
    item_name = Column(String, nullable=False)
    category = Column(String)
    brand = Column(String)
    condition = Column(String)
    description = Column(Text)
    image_paths = Column(JSON)
    pricing_data = Column(JSON)
    marketplace_recommendations = Column(JSON)
    listing_copy = Column(JSON)
    analysis_metadata = Column(JSON)
    status = Column(String, default='draft')
    posted_to = Column(JSON)
    posting_results = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PostgresDatabase:
    """PostgreSQL database implementation"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://localhost/marketplace_bot"
        )
        
        # Replace postgres:// with postgresql:// for SQLAlchemy
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif "asyncpg" not in self.database_url and "postgresql" in self.database_url:
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        self.engine = None
        self.async_session = None
        self.echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        logger.info(f"PostgreSQL database configured: {self.database_url.split('@')[-1]}")

    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=self.echo,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            
            self.async_session = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("PostgreSQL database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PostgreSQL database: {str(e)}")
            raise

    async def create_listing(self, **kwargs) -> Dict[str, Any]:
        """Create new listing"""
        try:
            # Generate ID if not provided
            if 'id' not in kwargs:
                import uuid
                kwargs['id'] = str(uuid.uuid4())
            
            # Ensure timestamps
            kwargs['created_at'] = datetime.now()
            kwargs['updated_at'] = datetime.now()
            
            listing = ItemListingModel(**kwargs)
            
            async with self.async_session() as session:
                session.add(listing)
                await session.commit()
                await session.refresh(listing)
                
                return self._model_to_dict(listing)
                
        except Exception as e:
            logger.error(f"Error creating listing: {str(e)}")
            raise

    async def get_listing(self, listing_id: str) -> Optional[Dict[str, Any]]:
        """Get listing by ID"""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(ItemListingModel).where(ItemListingModel.id == listing_id)
                )
                listing = result.scalar_one_or_none()
                
                if listing:
                    return self._model_to_dict(listing)
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
            async with self.async_session() as session:
                query = select(ItemListingModel)
                
                if status:
                    query = query.where(ItemListingModel.status == status)
                
                query = query.order_by(ItemListingModel.created_at.desc())
                query = query.limit(limit).offset(offset)
                
                result = await session.execute(query)
                listings = result.scalars().all()
                
                return [self._model_to_dict(listing) for listing in listings]
                
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
            updates['updated_at'] = datetime.now()
            
            async with self.async_session() as session:
                stmt = (
                    update(ItemListingModel)
                    .where(ItemListingModel.id == listing_id)
                    .values(**updates)
                )
                await session.execute(stmt)
                await session.commit()
                
                # Fetch updated listing
                return await self.get_listing(listing_id)
                
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
            async with self.async_session() as session:
                stmt = delete(ItemListingModel).where(ItemListingModel.id == listing_id)
                result = await session.execute(stmt)
                await session.commit()
                
                return result.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting listing {listing_id}: {str(e)}")
            raise

    async def search_listings(self, query: str) -> List[Dict[str, Any]]:
        """Search listings by query"""
        try:
            query_lower = f"%{query.lower()}%"
            
            async with self.async_session() as session:
                from sqlalchemy import or_, func
                
                stmt = select(ItemListingModel).where(
                    or_(
                        func.lower(ItemListingModel.item_name).like(query_lower),
                        func.lower(ItemListingModel.category).like(query_lower),
                        func.lower(ItemListingModel.brand).like(query_lower),
                        func.lower(ItemListingModel.description).like(query_lower)
                    )
                )
                
                result = await session.execute(stmt)
                listings = result.scalars().all()
                
                return [self._model_to_dict(listing) for listing in listings]
                
        except Exception as e:
            logger.error(f"Error searching listings: {str(e)}")
            raise

    def _model_to_dict(self, model: ItemListingModel) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary"""
        return {
            'id': model.id,
            'item_name': model.item_name,
            'category': model.category,
            'brand': model.brand,
            'condition': model.condition,
            'description': model.description,
            'image_paths': model.image_paths or [],
            'pricing_data': model.pricing_data or {},
            'marketplace_recommendations': model.marketplace_recommendations or [],
            'listing_copy': model.listing_copy or {},
            'analysis_metadata': model.analysis_metadata or {},
            'status': model.status,
            'posted_to': model.posted_to or [],
            'posting_results': model.posting_results or {},
            'created_at': model.created_at.isoformat() if model.created_at else None,
            'updated_at': model.updated_at.isoformat() if model.updated_at else None
        }

    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("PostgreSQL database connection closed")
