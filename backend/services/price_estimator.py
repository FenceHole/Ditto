"""
Price Estimator Service
Estimates optimal pricing based on market research and item attributes
Uses eBay SOLD listings for real market data
"""

import anthropic
import os
from typing import Dict, Any, Optional
import json
from .ebay_service import eBayService


class PriceEstimator:
    """Estimates item pricing using eBay sold data and AI analysis"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        self.ebay_service = eBayService()

    async def estimate_price(
        self,
        item_name: str,
        category: str,
        condition: str,
        brand: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate optimal pricing for an item using eBay SOLD listings

        Args:
            item_name: Name/description of the item
            category: Item category
            condition: Item condition (new, like-new, good, fair, poor)
            brand: Brand name if applicable
            attributes: Additional item attributes

        Returns:
            Dictionary with pricing recommendations based on real sold data
        """
        try:
            # Step 1: Get eBay sold listings data (REAL market data)
            search_query = f"{brand} {item_name}" if brand else item_name
            ebay_data = await self.ebay_service.search_sold_listings(
                keywords=search_query,
                condition=condition,
                max_results=50
            )

            # Step 2: Use AI to analyze and refine pricing with context
            if self.client and ebay_data.get('success'):
                pricing_data = await self._estimate_with_sold_data(
                    item_name, category, condition, brand, attributes, ebay_data
                )
            elif ebay_data.get('success'):
                # Have eBay data but no AI - use statistical analysis
                pricing_data = self._calculate_pricing_from_ebay(ebay_data, condition)
            elif self.client:
                # No eBay data but have AI - use AI estimates
                pricing_data = await self._estimate_without_ebay(
                    item_name, category, condition, brand, attributes
                )
            else:
                # No data sources available
                pricing_data = self._mock_pricing(item_name, condition)

            # Add eBay data source to response
            pricing_data['ebay_sold_data'] = ebay_data
            pricing_data['data_source'] = ebay_data.get('data_source', 'Estimated')

            return pricing_data

        except Exception as e:
            print(f"Error estimating price: {str(e)}")
            return self._mock_pricing(item_name, condition)

    async def _estimate_with_sold_data(
        self,
        item_name: str,
        category: str,
        condition: str,
        brand: Optional[str],
        attributes: Optional[Dict[str, Any]],
        ebay_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to analyze eBay sold data and provide intelligent pricing"""
        prompt = self._build_pricing_prompt_with_ebay(
            item_name, category, condition, brand, attributes, ebay_data
        )

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1524,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        pricing_data = self._parse_pricing_response(response_text)

        # Ensure we include eBay comparables
        if 'comparable_items' not in pricing_data:
            pricing_data['comparable_items'] = []

        # Add top eBay sold listings as comparables
        for listing in ebay_data.get('sold_listings', [])[:5]:
            pricing_data['comparable_items'].append({
                'description': listing['title'],
                'price': f"${listing['total_price']:.2f}",
                'source': f"eBay Sold - {listing['sold_date'][:10]}"
            })

        return pricing_data

    async def _estimate_without_ebay(
        self,
        item_name: str,
        category: str,
        condition: str,
        brand: Optional[str],
        attributes: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback to AI-only pricing when eBay data unavailable"""
        prompt = self._build_pricing_prompt(
            item_name, category, condition, brand, attributes
        )

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1524,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        return self._parse_pricing_response(response_text)

    def _calculate_pricing_from_ebay(
        self,
        ebay_data: Dict[str, Any],
        condition: str
    ) -> Dict[str, Any]:
        """Calculate pricing using eBay statistical data only"""
        median = ebay_data.get('median_price', 0)
        avg = ebay_data.get('average_price', 0)
        p25 = ebay_data.get('percentile_25', 0)
        p75 = ebay_data.get('percentile_75', 0)

        # Use median as base (more resistant to outliers)
        recommended_price = median

        # Quick sale at 25th percentile (priced to move)
        quick_sale_price = p25 * 0.95  # Slightly below 25th percentile

        return {
            "market_value_new": f"${p75:.2f}",
            "market_value_used": f"${median:.2f}",
            "recommended_price": round(recommended_price, 2),
            "price_range": {
                "min": round(p25, 2),
                "max": round(p75, 2)
            },
            "quick_sale_price": round(quick_sale_price, 2),
            "pricing_factors": [
                f"Based on {ebay_data.get('sold_count', 0)} actual eBay sales",
                f"Median sold price: ${median:.2f}",
                ebay_data.get('market_insight', '')
            ],
            "market_demand": self._calculate_demand(ebay_data),
            "turnover_estimate": self._estimate_turnover(ebay_data),
            "pricing_strategy": f"Priced at median of real sold items. {ebay_data.get('recent_sales_count', 0)} recent sales in last 30 days.",
            "comparable_items": [
                {
                    'description': listing['title'],
                    'price': f"${listing['total_price']:.2f}",
                    'source': f"eBay Sold - {listing['sold_date'][:10]}"
                }
                for listing in ebay_data.get('sold_listings', [])[:5]
            ]
        }

    def _calculate_demand(self, ebay_data: Dict[str, Any]) -> str:
        """Calculate market demand from eBay data"""
        sold_count = ebay_data.get('sold_count', 0)
        recent_count = ebay_data.get('recent_sales_count', 0)

        if recent_count > 10:
            return "high"
        elif recent_count > 5:
            return "medium"
        elif sold_count > 10:
            return "medium"
        else:
            return "low"

    def _estimate_turnover(self, ebay_data: Dict[str, Any]) -> str:
        """Estimate days to sell based on eBay activity"""
        recent_count = ebay_data.get('recent_sales_count', 0)

        if recent_count > 15:
            return "3-7 days (high activity)"
        elif recent_count > 8:
            return "7-14 days (moderate activity)"
        elif recent_count > 3:
            return "14-30 days (slower market)"
        else:
            return "30+ days (limited market)"

    def _build_pricing_prompt_with_ebay(
        self,
        item_name: str,
        category: str,
        condition: str,
        brand: Optional[str],
        attributes: Optional[Dict[str, Any]],
        ebay_data: Dict[str, Any]
    ) -> str:
        """Build pricing prompt WITH eBay sold data"""

        prompt = f"""You are a pricing expert for online marketplace listings. I have REAL eBay SOLD data (actual completed sales, not asking prices) for similar items.

Item Details:
- Item: {item_name}
- Category: {category}
- Condition: {condition}"""

        if brand:
            prompt += f"\n- Brand: {brand}"

        if attributes:
            prompt += f"\n- Attributes: {json.dumps(attributes, indent=2)}"

        # Add eBay sold data
        prompt += f"""

REAL EBAY SOLD DATA (Actual Completed Sales):
- Total Sold in Last 90 Days: {ebay_data.get('sold_count', 0)}
- Recent Sales (Last 30 Days): {ebay_data.get('recent_sales_count', 0)}
- Average Sold Price: ${ebay_data.get('average_price', 0):.2f}
- Median Sold Price: ${ebay_data.get('median_price', 0):.2f}
- Price Range: ${ebay_data.get('min_price', 0):.2f} - ${ebay_data.get('max_price', 0):.2f}
- 25th Percentile: ${ebay_data.get('percentile_25', 0):.2f}
- 75th Percentile: ${ebay_data.get('percentile_75', 0):.2f}
- Market Insight: {ebay_data.get('market_insight', '')}

Recent Sold Examples:"""

        # Add actual sold listings
        for i, listing in enumerate(ebay_data.get('sold_listings', [])[:5], 1):
            prompt += f"\n{i}. {listing['title']} - ${listing['total_price']:.2f} (Sold {listing['sold_date'][:10]}, {listing['condition']})"

        prompt += """

Based on this REAL sold data (not guesses!), provide pricing recommendations in JSON format:

{
  "market_value_new": "estimated retail price for new condition (USD)",
  "market_value_used": "typical used market value (USD)",
  "recommended_price": "your recommended listing price based on sold data (USD)",
  "price_range": {
    "min": "minimum suggested price (USD)",
    "max": "maximum suggested price (USD)"
  },
  "quick_sale_price": "price for fast turnover (USD)",
  "pricing_factors": [
    "factor 1 affecting price",
    "factor 2 affecting price"
  ],
  "market_demand": "high/medium/low",
  "turnover_estimate": "estimated days to sell at recommended price",
  "pricing_strategy": "explanation based on the SOLD data above"
}

Focus on:
1. Use the MEDIAN sold price as your primary reference (more reliable than average)
2. The 25th percentile is good for quick sales
3. Consider if recent sales trend higher or lower
4. Account for condition differences in the sold data
5. Factor in sales velocity (how many sold recently)

Provide realistic pricing that reflects what buyers ACTUALLY PAID, not seller hopes."""

        return prompt

    def _build_pricing_prompt(
        self,
        item_name: str,
        category: str,
        condition: str,
        brand: Optional[str],
        attributes: Optional[Dict[str, Any]]
    ) -> str:
        """Build pricing analysis prompt (fallback without eBay data)"""

        prompt = f"""You are a pricing expert for online marketplace listings. Analyze the following item and provide pricing recommendations.

Item Details:
- Item: {item_name}
- Category: {category}
- Condition: {condition}"""

        if brand:
            prompt += f"\n- Brand: {brand}"

        if attributes:
            prompt += f"\n- Attributes: {json.dumps(attributes, indent=2)}"

        prompt += """

Based on current market conditions, similar listings, and the item's attributes, provide pricing recommendations in JSON format:

{
  "market_value_new": "estimated retail price for new condition (USD)",
  "market_value_used": "typical used market value (USD)",
  "recommended_price": "your recommended listing price (USD)",
  "price_range": {
    "min": "minimum suggested price (USD)",
    "max": "maximum suggested price (USD)"
  },
  "quick_sale_price": "price for fast turnover (USD)",
  "pricing_factors": [
    "factor 1 affecting price",
    "factor 2 affecting price"
  ],
  "market_demand": "high/medium/low",
  "turnover_estimate": "estimated days to sell at recommended price",
  "pricing_strategy": "brief explanation of pricing recommendation",
  "comparable_items": [
    {
      "description": "similar item description",
      "price": "price (USD)",
      "source": "where it was listed"
    }
  ]
}

Focus on:
1. Current market prices for similar items
2. Condition-based pricing adjustments
3. Seasonal demand factors
4. Brand value impact
5. Quick sale vs. maximum value tradeoffs

Provide realistic, data-driven pricing that balances quick turnover with fair value."""

        return prompt

    def _parse_pricing_response(self, response_text: str) -> Dict[str, Any]:
        """Parse pricing response from Claude"""
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                pricing = json.loads(json_str)

                # Ensure numeric values are properly formatted
                if isinstance(pricing.get('recommended_price'), str):
                    pricing['recommended_price'] = self._parse_price(pricing['recommended_price'])
                if isinstance(pricing.get('quick_sale_price'), str):
                    pricing['quick_sale_price'] = self._parse_price(pricing['quick_sale_price'])

                return pricing
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            print(f"Error parsing pricing response: {str(e)}")
            return {
                "recommended_price": 0,
                "quick_sale_price": 0,
                "market_demand": "unknown",
                "pricing_strategy": "Could not determine pricing"
            }

    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        try:
            # Remove currency symbols and commas
            clean_price = price_str.replace('$', '').replace(',', '').strip()
            return float(clean_price)
        except:
            return 0.0

    def _mock_pricing(self, item_name: str, condition: str) -> Dict[str, Any]:
        """Mock pricing for testing"""
        base_price = 50.0

        # Adjust based on condition
        condition_multipliers = {
            "new": 1.0,
            "like-new": 0.85,
            "good": 0.70,
            "fair": 0.50,
            "poor": 0.30
        }
        multiplier = condition_multipliers.get(condition.lower(), 0.70)

        recommended = base_price * multiplier
        quick_sale = recommended * 0.85

        return {
            "market_value_new": "$50.00",
            "market_value_used": f"${recommended:.2f}",
            "recommended_price": recommended,
            "price_range": {
                "min": round(recommended * 0.80, 2),
                "max": round(recommended * 1.20, 2)
            },
            "quick_sale_price": quick_sale,
            "pricing_factors": [
                "Mock pricing - Set ANTHROPIC_API_KEY for real estimates",
                f"Condition: {condition}"
            ],
            "market_demand": "medium",
            "turnover_estimate": "7-14 days",
            "pricing_strategy": "This is mock data. Configure API key for real pricing analysis.",
            "comparable_items": []
        }
