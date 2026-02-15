"""
eBay Service
Handles eBay sold listings search and posting integration
"""

import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import base64


class eBayService:
    """eBay API integration for sold listings research and posting"""

    def __init__(self):
        self.app_id = os.getenv("EBAY_APP_ID")  # Client ID
        self.cert_id = os.getenv("EBAY_CERT_ID")  # Client Secret
        self.dev_id = os.getenv("EBAY_DEV_ID")
        self.auth_token = os.getenv("EBAY_AUTH_TOKEN")  # OAuth token

        self.sandbox = os.getenv("EBAY_SANDBOX", "false").lower() == "true"

        # API endpoints
        if self.sandbox:
            self.finding_api_url = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"
            self.trading_api_url = "https://api.sandbox.ebay.com/ws/api.dll"
            self.browse_api_url = "https://api.sandbox.ebay.com/buy/browse/v1"
        else:
            self.finding_api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
            self.trading_api_url = "https://api.ebay.com/ws/api.dll"
            self.browse_api_url = "https://api.ebay.com/buy/browse/v1"

        self.oauth_token = None
        self.token_expiry = None

    async def search_sold_listings(
        self,
        keywords: str,
        category_id: Optional[str] = None,
        condition: Optional[str] = None,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Search eBay SOLD listings (completed sales) for accurate pricing data

        Args:
            keywords: Search terms (item name, brand, model)
            category_id: eBay category ID (optional)
            condition: Item condition filter
            max_results: Maximum results to return (default 50)

        Returns:
            Dictionary with sold listings data and pricing analysis
        """
        if not self.app_id:
            return self._mock_sold_data(keywords)

        try:
            # Use Finding API to search completed/sold items
            params = {
                'OPERATION-NAME': 'findCompletedItems',
                'SERVICE-VERSION': '1.13.0',
                'SECURITY-APPNAME': self.app_id,
                'RESPONSE-DATA-FORMAT': 'JSON',
                'keywords': keywords,
                'paginationInput.entriesPerPage': min(max_results, 100),
                'sortOrder': 'EndTimeSoonest',  # Most recent sales first
            }

            # Build item filters
            filter_index = 0

            # Filter 1: Only sold items
            params[f'itemFilter({filter_index}).name'] = 'SoldItemsOnly'
            params[f'itemFilter({filter_index}).value'] = 'true'
            filter_index += 1

            # Filter 2: Condition
            if condition:
                ebay_condition = self._map_condition_to_ebay(condition)
                if ebay_condition:
                    params[f'itemFilter({filter_index}).name'] = 'Condition'
                    params[f'itemFilter({filter_index}).value'] = ebay_condition
                    filter_index += 1

            # Filter 3: Only listings with actual sales (not just ended)
            params[f'itemFilter({filter_index}).name'] = 'ListingType'
            params[f'itemFilter({filter_index}).value(0)'] = 'FixedPrice'
            params[f'itemFilter({filter_index}).value(1)'] = 'Auction'
            filter_index += 1

            # Make API request
            response = requests.get(self.finding_api_url, params=params)
            response.raise_for_status()

            data = response.json()

            # Parse results
            return self._parse_sold_listings(data, keywords)

        except Exception as e:
            print(f"Error searching eBay sold listings: {str(e)}")
            return self._mock_sold_data(keywords)

    def _parse_sold_listings(self, api_response: Dict, keywords: str) -> Dict[str, Any]:
        """Parse eBay API response and analyze sold listings"""
        try:
            search_result = api_response.get('findCompletedItemsResponse', [{}])[0]
            items = search_result.get('searchResult', [{}])[0].get('item', [])

            if not items:
                return {
                    'success': False,
                    'message': 'No sold listings found',
                    'sold_count': 0,
                    'average_price': 0,
                    'sold_listings': []
                }

            sold_listings = []
            prices = []

            for item in items:
                try:
                    # Extract item details
                    title = item.get('title', [''])[0]
                    item_id = item.get('itemId', [''])[0]

                    # Get selling price
                    selling_status = item.get('sellingStatus', [{}])[0]
                    price_info = selling_status.get('currentPrice', [{}])[0]
                    price = float(price_info.get('__value__', 0))
                    currency = price_info.get('@currencyId', 'USD')

                    # Get shipping cost
                    shipping_info = item.get('shippingInfo', [{}])[0]
                    shipping_cost_info = shipping_info.get('shippingServiceCost', [{}])[0]
                    shipping_cost = float(shipping_cost_info.get('__value__', 0))

                    # Get condition
                    condition_info = item.get('condition', [{}])[0]
                    condition_display = condition_info.get('conditionDisplayName', ['Used'])[0]

                    # Get end time (sale date)
                    listing_info = item.get('listingInfo', [{}])[0]
                    end_time = listing_info.get('endTime', [''])[0]

                    # Get image
                    gallery_url = item.get('galleryURL', [''])[0]

                    # Get view/listing URL
                    view_url = item.get('viewItemURL', [''])[0]

                    # Only include actual sales (some completed items don't sell)
                    sold_date = selling_status.get('sellingState', [''])[0]
                    if sold_date != 'EndedWithSales':
                        continue

                    total_price = price + shipping_cost
                    prices.append(total_price)

                    sold_listings.append({
                        'title': title,
                        'item_id': item_id,
                        'price': price,
                        'shipping_cost': shipping_cost,
                        'total_price': total_price,
                        'currency': currency,
                        'condition': condition_display,
                        'sold_date': end_time,
                        'image_url': gallery_url,
                        'listing_url': view_url
                    })

                except Exception as e:
                    print(f"Error parsing item: {str(e)}")
                    continue

            if not prices:
                return {
                    'success': False,
                    'message': 'No actual sales found (only ended listings)',
                    'sold_count': 0,
                    'average_price': 0,
                    'sold_listings': []
                }

            # Calculate pricing statistics
            prices.sort()
            count = len(prices)

            avg_price = sum(prices) / count
            median_price = prices[count // 2] if count > 0 else 0
            min_price = min(prices)
            max_price = max(prices)

            # Calculate price percentiles for better recommendations
            p25_price = prices[int(count * 0.25)] if count > 0 else 0
            p75_price = prices[int(count * 0.75)] if count > 0 else 0

            # Get recent sales (last 30 days)
            recent_cutoff = datetime.now() - timedelta(days=30)
            recent_sales = [
                listing for listing in sold_listings
                if self._parse_ebay_date(listing['sold_date']) > recent_cutoff
            ]

            return {
                'success': True,
                'keywords': keywords,
                'sold_count': count,
                'recent_sales_count': len(recent_sales),
                'average_price': round(avg_price, 2),
                'median_price': round(median_price, 2),
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2),
                'percentile_25': round(p25_price, 2),
                'percentile_75': round(p75_price, 2),
                'price_range': {
                    'low': round(min_price, 2),
                    'high': round(max_price, 2),
                    'typical': round(median_price, 2)
                },
                'market_insight': self._generate_market_insight(prices, recent_sales, count),
                'sold_listings': sold_listings[:20],  # Return top 20 for reference
                'data_source': 'eBay Sold Listings (Real Sales Data)'
            }

        except Exception as e:
            print(f"Error parsing sold listings: {str(e)}")
            return self._mock_sold_data(keywords)

    def _generate_market_insight(
        self,
        prices: List[float],
        recent_sales: List[Dict],
        total_count: int
    ) -> str:
        """Generate insight about market conditions based on sold data"""

        avg_price = sum(prices) / len(prices)
        recent_avg = sum(s['total_price'] for s in recent_sales) / len(recent_sales) if recent_sales else avg_price

        # Determine market activity
        if total_count > 30:
            activity = "Very active market with strong demand"
        elif total_count > 15:
            activity = "Moderate market activity"
        else:
            activity = "Limited sales history - niche item"

        # Price trend
        if recent_avg > avg_price * 1.1:
            trend = "Prices trending UP recently"
        elif recent_avg < avg_price * 0.9:
            trend = "Prices trending DOWN recently"
        else:
            trend = "Prices stable"

        # Price spread
        price_range = max(prices) - min(prices)
        spread_ratio = price_range / avg_price if avg_price > 0 else 0

        if spread_ratio > 0.5:
            spread = "Wide price variation - condition/features matter a lot"
        else:
            spread = "Consistent pricing across listings"

        return f"{activity}. {trend}. {spread}."

    def _parse_ebay_date(self, date_str: str) -> datetime:
        """Parse eBay date format to datetime"""
        try:
            # eBay format: 2024-01-15T14:30:00.000Z
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now()

    def _map_condition_to_ebay(self, condition: str) -> Optional[str]:
        """Map internal condition to eBay condition IDs"""
        condition_map = {
            'new': '1000',  # New
            'like-new': '1500',  # New other
            'good': '3000',  # Used
            'fair': '3000',  # Used
            'poor': '7000'  # For parts or not working
        }
        return condition_map.get(condition.lower())

    def _mock_sold_data(self, keywords: str) -> Dict[str, Any]:
        """Mock sold data for testing without API credentials"""
        return {
            'success': False,
            'message': 'eBay API not configured - Set EBAY_APP_ID to get real sold data',
            'keywords': keywords,
            'sold_count': 0,
            'average_price': 0,
            'median_price': 0,
            'sold_listings': [],
            'data_source': 'Mock Data - Configure eBay API for real pricing'
        }

    async def get_oauth_token(self) -> Optional[str]:
        """Get OAuth token for eBay API"""
        if self.oauth_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.oauth_token

        if not self.app_id or not self.cert_id:
            return None

        try:
            # Get application token (for non-user specific operations)
            auth_string = f"{self.app_id}:{self.cert_id}"
            auth_bytes = base64.b64encode(auth_string.encode('utf-8'))
            auth_header = f"Basic {auth_bytes.decode('utf-8')}"

            token_url = "https://api.ebay.com/identity/v1/oauth2/token"
            if self.sandbox:
                token_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': auth_header
            }

            data = {
                'grant_type': 'client_credentials',
                'scope': 'https://api.ebay.com/oauth/api_scope'
            }

            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.oauth_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 7200)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)

            return self.oauth_token

        except Exception as e:
            print(f"Error getting eBay OAuth token: {str(e)}")
            return None

    async def post_item(self, item: Any) -> Dict[str, Any]:
        """
        Post item to eBay

        Note: eBay posting requires user OAuth token and is more complex
        This is a placeholder for future implementation
        """
        return {
            'status': 'not_implemented',
            'message': 'eBay posting requires user authentication and listing details. Use eBay UI for now.',
            'listing_data': {
                'title': item.listing_copy.get('title'),
                'description': item.listing_copy.get('ebay_copy', item.description),
                'price': item.pricing_data.get('recommended_price'),
                'condition': item.condition
            }
        }
