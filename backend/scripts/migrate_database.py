#!/usr/bin/env python3
"""
Database Migration Script
Migrates data from JSON database to PostgreSQL or MongoDB
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import Database
from models.database_postgres import PostgresDatabase
from models.database_mongo import MongoDatabase
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def migrate_json_to_postgres(json_db_path: str, postgres_url: str):
    """Migrate from JSON to PostgreSQL"""
    logger.info("Starting migration from JSON to PostgreSQL...")
    
    # Load JSON data
    json_db = Database(json_db_path)
    await json_db.initialize()
    
    # Initialize PostgreSQL
    postgres_db = PostgresDatabase(postgres_url)
    await postgres_db.initialize()
    
    # Migrate listings
    count = 0
    for listing_id, listing in json_db.listings.items():
        try:
            data = listing.to_dict()
            await postgres_db.create_listing(**data)
            count += 1
            logger.info(f"Migrated listing {count}: {listing_id}")
        except Exception as e:
            logger.error(f"Error migrating listing {listing_id}: {str(e)}")
    
    logger.info(f"Migration complete! Migrated {count} listings to PostgreSQL")
    await postgres_db.close()


async def migrate_json_to_mongo(json_db_path: str, mongo_url: str):
    """Migrate from JSON to MongoDB"""
    logger.info("Starting migration from JSON to MongoDB...")
    
    # Load JSON data
    json_db = Database(json_db_path)
    await json_db.initialize()
    
    # Initialize MongoDB
    mongo_db = MongoDatabase(mongo_url)
    await mongo_db.initialize()
    
    # Migrate listings
    count = 0
    for listing_id, listing in json_db.listings.items():
        try:
            data = listing.to_dict()
            await mongo_db.create_listing(**data)
            count += 1
            logger.info(f"Migrated listing {count}: {listing_id}")
        except Exception as e:
            logger.error(f"Error migrating listing {listing_id}: {str(e)}")
    
    logger.info(f"Migration complete! Migrated {count} listings to MongoDB")
    await mongo_db.close()


async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate database')
    parser.add_argument('--from', dest='source', required=True, 
                      help='Source database type (json)')
    parser.add_argument('--to', dest='target', required=True,
                      help='Target database type (postgres or mongodb)')
    parser.add_argument('--json-path', default='./data/listings.json',
                      help='Path to JSON database file')
    parser.add_argument('--target-url', required=True,
                      help='Target database URL')
    
    args = parser.parse_args()
    
    if args.source != 'json':
        logger.error("Currently only 'json' is supported as source database")
        return
    
    if args.target == 'postgres':
        await migrate_json_to_postgres(args.json_path, args.target_url)
    elif args.target == 'mongodb':
        await migrate_json_to_mongo(args.json_path, args.target_url)
    else:
        logger.error(f"Unknown target database: {args.target}")


if __name__ == "__main__":
    asyncio.run(main())
