"""
Facebook Listing Formatter

IMPORTANT: Facebook Marketplace has NO public API for posting personal listings.
Any code that claims to "auto-post to Facebook Marketplace" via the Graph API does
not work for personal selling — that path is intentionally closed by Facebook.

So this module does NOT call Facebook. It only formats the finished listing into a
clean, paste-ready block. You (or an automation driving a DEDICATED account) paste
that into the Marketplace "Create listing" form.

For opt-in browser automation against a dedicated account, see
`services/playwright_poster.py` (only runs when ENABLE_BROWSER_POSTER=true).
"""

from typing import Dict, Any


class FacebookPoster:
    """Formats a saved item into a paste-ready Marketplace listing (no network calls)."""

    async def preview_listing(self, item: Any) -> Dict[str, Any]:
        """
        Return a preview of how the listing should look. No posting happens.
        """
        price = item.pricing_data.get("recommended_price", 0)
        try:
            price_str = f"${float(price):.0f}"
        except (TypeError, ValueError):
            price_str = str(price)

        return {
            "title": item.listing_copy.get("title", item.item_name),
            "description": item.listing_copy.get(
                "facebook_copy", item.listing_copy.get("description", item.description)
            ),
            "price": price_str,
            "condition": item.condition,
            "photos": item.image_paths,
            "category": item.category,
            "how_to_post": (
                "Copy this into Facebook Marketplace > Create new listing > Item for sale. "
                "Add the photos, paste the title/price/description, then publish."
            ),
        }
