"""
Facebook Marketplace Poster Service
Handles posting to Facebook Marketplace via Graph API
"""

import os
from typing import Dict, Any, Optional
import requests


class FacebookPoster:
    """Posts listings to Facebook Marketplace"""

    def __init__(self):
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        self.graph_api_url = "https://graph.facebook.com/v18.0"

        if not self.access_token:
            print("WARNING: FACEBOOK_ACCESS_TOKEN not set. Facebook posting will be disabled.")

    async def post_item(self, item: Any) -> Dict[str, Any]:
        """
        Post item to Facebook Marketplace

        Args:
            item: Item listing object

        Returns:
            Posting result with URL and status
        """
        if not self.access_token:
            return {
                "status": "error",
                "message": "Facebook access token not configured",
                "preview_mode": True
            }

        try:
            # Upload photos first
            photo_ids = await self._upload_photos(item.image_paths)

            # Create marketplace listing
            listing_data = {
                "name": item.listing_copy.get("title", item.item_name),
                "description": item.listing_copy.get("facebook_copy", item.description),
                "price": item.pricing_data.get("recommended_price", 0) * 100,  # Convert to cents
                "currency": "USD",
                "condition": self._map_condition(item.condition),
                "availability": "AVAILABLE",
                "photos": photo_ids
            }

            # Post to marketplace
            response = requests.post(
                f"{self.graph_api_url}/{self.page_id}/marketplace_listings",
                params={"access_token": self.access_token},
                json=listing_data
            )

            if response.status_code == 200:
                result = response.json()
                listing_id = result.get("id")

                return {
                    "status": "success",
                    "listing_id": listing_id,
                    "url": f"https://www.facebook.com/marketplace/item/{listing_id}",
                    "posted_at": "now"
                }
            else:
                return {
                    "status": "error",
                    "message": response.text,
                    "code": response.status_code
                }

        except Exception as e:
            print(f"Error posting to Facebook: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def preview_listing(self, item: Any) -> Dict[str, Any]:
        """
        Generate preview of how listing would appear

        Args:
            item: Item listing object

        Returns:
            Preview data
        """
        return {
            "title": item.listing_copy.get("title", item.item_name),
            "description": item.listing_copy.get("facebook_copy", item.description),
            "price": f"${item.pricing_data.get('recommended_price', 0):.2f}",
            "condition": item.condition,
            "photos": item.image_paths,
            "location": "Your Location",  # Would be configured
            "category": item.category
        }

    async def _upload_photos(self, image_paths: list) -> list:
        """
        Upload photos to Facebook

        Args:
            image_paths: List of local image paths

        Returns:
            List of Facebook photo IDs
        """
        if not self.access_token:
            return []

        photo_ids = []

        for img_path in image_paths[:10]:  # Facebook allows max 10 photos
            try:
                with open(img_path, 'rb') as photo:
                    files = {'source': photo}
                    params = {
                        'access_token': self.access_token,
                        'published': 'false'  # Upload but don't publish yet
                    }

                    response = requests.post(
                        f"{self.graph_api_url}/{self.page_id}/photos",
                        params=params,
                        files=files
                    )

                    if response.status_code == 200:
                        photo_data = response.json()
                        photo_ids.append(photo_data['id'])

            except Exception as e:
                print(f"Error uploading photo {img_path}: {str(e)}")
                continue

        return photo_ids

    def _map_condition(self, condition: str) -> str:
        """Map internal condition to Facebook condition values"""
        condition_map = {
            "new": "NEW",
            "like-new": "LIKE_NEW",
            "good": "GOOD",
            "fair": "FAIR",
            "poor": "POOR"
        }
        return condition_map.get(condition.lower(), "GOOD")

    async def update_listing(self, listing_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing Facebook listing"""
        if not self.access_token:
            return {"status": "error", "message": "Not configured"}

        try:
            response = requests.post(
                f"{self.graph_api_url}/{listing_id}",
                params={"access_token": self.access_token},
                json=updates
            )

            return {
                "status": "success" if response.status_code == 200 else "error",
                "response": response.json()
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def delete_listing(self, listing_id: str) -> Dict[str, Any]:
        """Delete Facebook listing"""
        if not self.access_token:
            return {"status": "error", "message": "Not configured"}

        try:
            response = requests.delete(
                f"{self.graph_api_url}/{listing_id}",
                params={"access_token": self.access_token}
            )

            return {
                "status": "success" if response.status_code == 200 else "error"
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
