"""
Facebook Marketplace Poster Service
Handles posting to Facebook Marketplace via Graph API
"""

import os
from typing import Dict, Any, Optional
import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class FacebookPoster:
    """Posts listings to Facebook Marketplace"""

    def __init__(self):
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        self.graph_api_url = "https://graph.facebook.com/v18.0"

        if not self.access_token:
            logger.warning("Facebook access token not configured. Posting will be disabled.")

    async def post_item(self, item: Any) -> Dict[str, Any]:
        """
        Post item to Facebook Marketplace

        Args:
            item: Item listing object

        Returns:
            Posting result with URL and status
        """
        if not self.access_token:
            logger.warning("Facebook posting attempted without access token configured")
            return {
                "status": "error",
                "message": "Facebook access token not configured",
                "preview_mode": True
            }

        try:
            # Convert item dict to object-like access if needed
            if isinstance(item, dict):
                class DictObj:
                    def __init__(self, d):
                        self.__dict__.update(d)
                    def get(self, key, default=None):
                        return self.__dict__.get(key, default)
                item = DictObj(item)
            
            # Upload photos first
            photo_ids = await self._upload_photos(item.image_paths)
            
            if not photo_ids:
                logger.warning(f"No photos uploaded for item, cannot post to Facebook")
                return {
                    "status": "error",
                    "message": "Failed to upload photos to Facebook"
                }

            # Create marketplace listing
            listing_data = {
                "name": item.listing_copy.get("title", item.item_name),
                "description": item.listing_copy.get("facebook_copy", item.description),
                "price": int(item.pricing_data.get("recommended_price", 0) * 100),  # Convert to cents
                "currency": "USD",
                "condition": self._map_condition(item.condition),
                "availability": "AVAILABLE",
                "photos": photo_ids
            }

            logger.info(f"Posting to Facebook Marketplace: {listing_data['name']}")

            # Post to marketplace
            response = requests.post(
                f"{self.graph_api_url}/{self.page_id}/marketplace_listings",
                params={"access_token": self.access_token},
                json=listing_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                listing_id = result.get("id")

                logger.info(f"Successfully posted to Facebook: {listing_id}")
                return {
                    "status": "success",
                    "listing_id": listing_id,
                    "url": f"https://www.facebook.com/marketplace/item/{listing_id}",
                    "posted_at": "now"
                }
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', response.text)
                logger.error(f"Facebook API error {response.status_code}: {error_msg}")
                return {
                    "status": "error",
                    "message": f"Facebook API error: {error_msg}",
                    "code": response.status_code
                }

        except requests.exceptions.Timeout:
            logger.error("Facebook API timeout")
            return {
                "status": "error",
                "message": "Request to Facebook timed out"
            }
        except requests.exceptions.ConnectionError:
            logger.error("Facebook API connection error")
            return {
                "status": "error",
                "message": "Could not connect to Facebook API"
            }
        except Exception as e:
            logger.error(f"Error posting to Facebook: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }

    async def preview_listing(self, item: Any) -> Dict[str, Any]:
        """
        Generate preview of how listing would appear

        Args:
            item: Item listing object or dict

        Returns:
            Preview data
        """
        # Convert dict to object-like access if needed
        if isinstance(item, dict):
            class DictObj:
                def __init__(self, d):
                    self.__dict__.update(d)
                def get(self, key, default=None):
                    return self.__dict__.get(key, default)
            item = DictObj(item)
        
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
                        files=files,
                        timeout=30
                    )

                    if response.status_code == 200:
                        photo_data = response.json()
                        photo_ids.append(photo_data['id'])
                        logger.debug(f"Uploaded photo: {photo_data['id']}")
                    else:
                        logger.warning(f"Failed to upload photo {img_path}: {response.status_code}")

            except FileNotFoundError:
                logger.error(f"Photo file not found: {img_path}")
                continue
            except Exception as e:
                logger.error(f"Error uploading photo {img_path}: {str(e)}")
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
            logger.warning("Facebook update attempted without access token")
            return {"status": "error", "message": "Not configured"}

        try:
            response = requests.post(
                f"{self.graph_api_url}/{listing_id}",
                params={"access_token": self.access_token},
                json=updates,
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"Successfully updated Facebook listing: {listing_id}")
                return {
                    "status": "success",
                    "response": response.json()
                }
            else:
                logger.error(f"Failed to update Facebook listing: {response.status_code}")
                return {
                    "status": "error",
                    "response": response.json()
                }

        except Exception as e:
            logger.error(f"Error updating Facebook listing: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def delete_listing(self, listing_id: str) -> Dict[str, Any]:
        """Delete Facebook listing"""
        if not self.access_token:
            logger.warning("Facebook delete attempted without access token")
            return {"status": "error", "message": "Not configured"}

        try:
            response = requests.delete(
                f"{self.graph_api_url}/{listing_id}",
                params={"access_token": self.access_token},
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"Successfully deleted Facebook listing: {listing_id}")
                return {"status": "success"}
            else:
                logger.error(f"Failed to delete Facebook listing: {response.status_code}")
                return {"status": "error"}

        except Exception as e:
            logger.error(f"Error deleting Facebook listing: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
