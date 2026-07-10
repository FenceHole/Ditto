"""
Marketplace Bot Analyzer - Main API Server
FastAPI-based backend for item analysis and marketplace posting
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from datetime import datetime
import json

from services.image_analyzer import ImageAnalyzer
from services.price_estimator import PriceEstimator
from services.marketplace_selector import MarketplaceSelector
from services.listing_generator import ListingGenerator
from services.facebook_poster import FacebookPoster
from services.storage_manager import StorageManager
from models.database import Database, ItemListing

app = FastAPI(
    title="Marketplace Bot Analyzer",
    description="AI-powered marketplace listing automation",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
image_analyzer = ImageAnalyzer()
price_estimator = PriceEstimator()
marketplace_selector = MarketplaceSelector()
listing_generator = ListingGenerator()
facebook_poster = FacebookPoster()
storage_manager = StorageManager()
db = Database()


class AnalyzeRequest(BaseModel):
    """Request model for item analysis"""
    condition: Optional[str] = "good"
    additional_notes: Optional[str] = None


class PostRequest(BaseModel):
    """Request model for posting to marketplace"""
    item_id: str
    marketplaces: List[str]
    auto_post: bool = False


def check_api_key(x_api_key: Optional[str] = Header(default=None)):
    """
    Simple API-key gate so an external caller (e.g. the user's 'nessie'
    automation stack) can authenticate. If APP_API_KEY is unset, access is
    open — this keeps local/dev use frictionless.
    """
    expected = os.getenv("APP_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    return True


def build_ready_to_post(item_name: str, price: Any, condition: str,
                        listing_copy: Dict[str, Any]) -> str:
    """
    Assemble a single copy-paste-ready block for Facebook Marketplace.
    This is the reliable deliverable: paste it into the Marketplace listing form.
    """
    title = listing_copy.get("title") or item_name
    body = listing_copy.get("facebook_copy") or listing_copy.get("description") or ""
    try:
        price_str = f"${float(price):.0f}"
    except (TypeError, ValueError):
        price_str = str(price)

    lines = [
        f"TITLE: {title}",
        f"PRICE: {price_str}",
        f"CONDITION: {condition}",
        "",
        body.strip(),
    ]
    return "\n".join(lines).strip()


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        await db.initialize()
        print("✓ Marketplace Bot Analyzer API started successfully")
    except Exception as e:
        print(f"⚠️ Warning: Database initialization failed: {str(e)}")
        print("⚠️ App will continue but data persistence may not work")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Marketplace Bot Analyzer",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/upload")
async def upload_images(
    files: List[UploadFile] = File(...),
    condition: str = "good",
    additional_notes: Optional[str] = None
):
    """
    Upload item photos for analysis

    Args:
        files: List of image files to analyze
        condition: Item condition (new, like-new, good, fair, poor)
        additional_notes: Any additional context about the item

    Returns:
        Analysis results with pricing and marketplace recommendations
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")

        if len(files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 images allowed per upload"
            )

        # Save uploaded images
        image_paths = []
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not an image"
                )

            file_path = await storage_manager.save_upload(file)
            image_paths.append(file_path)

        # Analyze images to identify the item
        print(f"Analyzing {len(image_paths)} images...")
        analysis_result = await image_analyzer.analyze_images(
            image_paths,
            additional_context=additional_notes
        )

        if not analysis_result.get("identified"):
            raise HTTPException(
                status_code=422,
                detail="Could not identify item from images"
            )

        # Estimate pricing
        print(f"Estimating price for: {analysis_result['item_name']}")
        pricing_data = await price_estimator.estimate_price(
            item_name=analysis_result['item_name'],
            category=analysis_result['category'],
            condition=condition,
            brand=analysis_result.get('brand'),
            attributes=analysis_result.get('attributes', {})
        )

        # Determine best marketplaces
        print("Selecting optimal marketplaces...")
        marketplace_recommendations = await marketplace_selector.select_marketplaces(
            category=analysis_result['category'],
            estimated_price=pricing_data['recommended_price'],
            item_type=analysis_result['item_name'],
            ebay_sold_data=pricing_data.get('ebay_sold_data')
        )

        # Generate listing copy
        print("Generating listing copy...")
        listing_copy = await listing_generator.generate_listing(
            item_name=analysis_result['item_name'],
            description=analysis_result['description'],
            condition=condition,
            price=pricing_data['recommended_price'],
            features=analysis_result.get('features', []),
            additional_notes=additional_notes
        )

        # Save to database
        item_listing = await db.create_listing(
            item_name=analysis_result['item_name'],
            category=analysis_result['category'],
            brand=analysis_result.get('brand'),
            condition=condition,
            description=analysis_result['description'],
            image_paths=image_paths,
            pricing_data=pricing_data,
            marketplace_recommendations=marketplace_recommendations,
            listing_copy=listing_copy,
            analysis_metadata=analysis_result
        )

        return {
            "success": True,
            "item_id": item_listing.id,
            "analysis": {
                "item_name": analysis_result['item_name'],
                "category": analysis_result['category'],
                "brand": analysis_result.get('brand'),
                "description": analysis_result['description'],
                "features": analysis_result.get('features', []),
                "condition": condition
            },
            "pricing": pricing_data,
            "marketplaces": marketplace_recommendations,
            "listing": listing_copy,
            "images": image_paths
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload_images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze(
    files: List[UploadFile] = File(...),
    condition: str = "good",
    notes: Optional[str] = None,
    x_api_key: Optional[str] = Header(default=None),
):
    """
    Clean integration endpoint for external automation (e.g. the user's 'nessie'
    stack). Photos in -> one finished, paste-ready listing out.

    Auth: send header `X-API-Key: <APP_API_KEY>` (only enforced if APP_API_KEY is set).

    Returns a flat, predictable JSON object:
        {
          success, item_id, item_name, category, condition,
          price, quick_sale_price, title, description, ready_to_post
        }
    `ready_to_post` is a single text block to paste straight into the
    Facebook Marketplace "Create listing" form.
    """
    # Auth gate
    check_api_key(x_api_key)

    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 images allowed")

        # Save images
        image_paths = []
        for file in files:
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not an image"
                )
            image_paths.append(await storage_manager.save_upload(file))

        # Identify item
        analysis_result = await image_analyzer.analyze_images(
            image_paths, additional_context=notes
        )
        if not analysis_result.get("identified"):
            raise HTTPException(status_code=422, detail="Could not identify item from images")

        # Price it
        pricing_data = await price_estimator.estimate_price(
            item_name=analysis_result["item_name"],
            category=analysis_result["category"],
            condition=condition,
            brand=analysis_result.get("brand"),
            attributes=analysis_result.get("attributes", {}),
        )

        # Rank marketplaces (used for internal record; Facebook is the primary target)
        marketplace_recommendations = await marketplace_selector.select_marketplaces(
            category=analysis_result["category"],
            estimated_price=pricing_data.get("recommended_price", 0),
            item_type=analysis_result["item_name"],
            ebay_sold_data=pricing_data.get("ebay_sold_data"),
        )

        # Write the listing copy
        listing_copy = await listing_generator.generate_listing(
            item_name=analysis_result["item_name"],
            description=analysis_result["description"],
            condition=condition,
            price=pricing_data.get("recommended_price", 0),
            features=analysis_result.get("features", []),
            additional_notes=notes,
        )

        ready_to_post = build_ready_to_post(
            analysis_result["item_name"],
            pricing_data.get("recommended_price", 0),
            condition,
            listing_copy,
        )

        # Persist so /api/post and history can reference it
        item_listing = await db.create_listing(
            item_name=analysis_result["item_name"],
            category=analysis_result["category"],
            brand=analysis_result.get("brand"),
            condition=condition,
            description=analysis_result["description"],
            image_paths=image_paths,
            pricing_data=pricing_data,
            marketplace_recommendations=marketplace_recommendations,
            listing_copy=listing_copy,
            analysis_metadata=analysis_result,
        )

        return {
            "success": True,
            "item_id": item_listing.id,
            "item_name": analysis_result["item_name"],
            "category": analysis_result["category"],
            "condition": condition,
            "price": pricing_data.get("recommended_price", 0),
            "quick_sale_price": pricing_data.get("quick_sale_price", 0),
            "title": listing_copy.get("title", analysis_result["item_name"]),
            "description": listing_copy.get("facebook_copy",
                                            listing_copy.get("description", "")),
            "ready_to_post": ready_to_post,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/post")
async def post_to_marketplaces(
    request: PostRequest,
    background_tasks: BackgroundTasks
):
    """
    Prepare a saved item for posting.

    NOTE: Facebook Marketplace has no public API for posting personal listings,
    so this does NOT call Facebook. It returns the finished, paste-ready listing
    (`ready_to_post`) that you — or your automation driving a DEDICATED account —
    paste into the Marketplace "Create listing" form.

    An optional browser-automation poster exists (services/playwright_poster.py)
    and only runs when ENABLE_BROWSER_POSTER=true, targeting the dedicated account.
    """
    try:
        item = await db.get_listing(request.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        ready_to_post = build_ready_to_post(
            item.item_name,
            item.pricing_data.get("recommended_price", 0),
            item.condition,
            item.listing_copy,
        )

        posting_results = {
            "status": "ready",
            "method": "manual_paste",
            "ready_to_post": ready_to_post,
        }

        # Opt-in browser automation for the dedicated account only.
        if os.getenv("ENABLE_BROWSER_POSTER", "false").lower() == "true":
            try:
                from services.playwright_poster import PlaywrightPoster
                poster = PlaywrightPoster()
                posting_results["browser_post"] = await poster.post_item(item)
            except Exception as e:
                posting_results["browser_post"] = {"status": "error", "message": str(e)}

        await db.update_listing_status(
            request.item_id,
            posted_to=request.marketplaces,
            posting_results=posting_results
        )

        return {
            "success": True,
            "item_id": request.item_id,
            "results": posting_results
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in post_to_marketplaces: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/listings")
async def get_listings(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Retrieve saved listings

    Args:
        status: Filter by status (draft, posted, sold)
        limit: Number of results to return
        offset: Pagination offset

    Returns:
        List of listings
    """
    try:
        listings = await db.get_listings(
            status=status,
            limit=limit,
            offset=offset
        )

        return {
            "success": True,
            "listings": listings,
            "count": len(listings)
        }

    except Exception as e:
        print(f"Error in get_listings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/listings/{item_id}")
async def get_listing(item_id: str):
    """Get specific listing by ID"""
    try:
        item = await db.get_listing(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Listing not found")

        return {
            "success": True,
            "listing": item
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_listing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/listings/{item_id}")
async def update_listing(
    item_id: str,
    updates: Dict[str, Any]
):
    """Update listing details"""
    try:
        updated_item = await db.update_listing(item_id, updates)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Listing not found")

        return {
            "success": True,
            "listing": updated_item
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_listing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/listings/{item_id}")
async def delete_listing(item_id: str):
    """Delete a listing"""
    try:
        success = await db.delete_listing(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Listing not found")

        return {
            "success": True,
            "message": "Listing deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_listing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
