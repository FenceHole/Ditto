"""
Price Estimator Service
Estimates optimal pricing based on market research and item attributes
"""

import anthropic
import os
from typing import Dict, Any, Optional
import json


class PriceEstimator:
    """Estimates item pricing using market research and AI analysis"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    async def estimate_price(
        self,
        item_name: str,
        category: str,
        condition: str,
        brand: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate optimal pricing for an item

        Args:
            item_name: Name/description of the item
            category: Item category
            condition: Item condition (new, like-new, good, fair, poor)
            brand: Brand name if applicable
            attributes: Additional item attributes

        Returns:
            Dictionary with pricing recommendations
        """
        if not self.client:
            return self._mock_pricing(item_name, condition)

        try:
            # Build pricing research prompt
            prompt = self._build_pricing_prompt(
                item_name, category, condition, brand, attributes
            )

            # Use Claude to research and estimate pricing
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1524,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text

            # Parse pricing response
            pricing_data = self._parse_pricing_response(response_text)

            return pricing_data

        except Exception as e:
            print(f"Error estimating price: {str(e)}")
            return self._mock_pricing(item_name, condition)

    def _build_pricing_prompt(
        self,
        item_name: str,
        category: str,
        condition: str,
        brand: Optional[str],
        attributes: Optional[Dict[str, Any]]
    ) -> str:
        """Build pricing analysis prompt"""

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
