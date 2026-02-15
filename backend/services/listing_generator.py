"""
Listing Generator Service
Creates compelling marketplace listing copy
"""

import anthropic
import os
from typing import List, Dict, Any, Optional


class ListingGenerator:
    """Generates optimized listing copy for marketplaces"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    async def generate_listing(
        self,
        item_name: str,
        description: str,
        condition: str,
        price: float,
        features: List[str],
        additional_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate compelling listing copy

        Args:
            item_name: Item name
            description: Item description from analysis
            condition: Item condition
            price: Listing price
            features: List of item features
            additional_notes: Additional context

        Returns:
            Dictionary with listing copy for different platforms
        """
        if not self.client:
            return self._mock_listing(item_name, description, condition, price)

        try:
            prompt = self._build_listing_prompt(
                item_name, description, condition, price, features, additional_notes
            )

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text

            # Parse the listing copy
            listing_data = self._parse_listing_response(response_text)

            return listing_data

        except Exception as e:
            print(f"Error generating listing: {str(e)}")
            return self._mock_listing(item_name, description, condition, price)

    def _build_listing_prompt(
        self,
        item_name: str,
        description: str,
        condition: str,
        price: float,
        features: List[str],
        additional_notes: Optional[str]
    ) -> str:
        """Build prompt for listing generation"""

        prompt = f"""You are an expert marketplace listing writer. Create compelling, honest, and effective listing copy.

Item Details:
- Item: {item_name}
- Description: {description}
- Condition: {condition}
- Price: ${price:.2f}
- Features: {', '.join(features) if features else 'N/A'}"""

        if additional_notes:
            prompt += f"\n- Additional Notes: {additional_notes}"

        prompt += """

Create optimized listing copy in JSON format:

{
  "title": "attention-grabbing title (60 chars max)",
  "description": "detailed description emphasizing value and features",
  "facebook_copy": "optimized for Facebook Marketplace (casual, local focus)",
  "short_description": "brief 1-2 sentence summary",
  "hashtags": ["relevant", "hashtags"],
  "keywords": ["SEO", "keywords"],
  "bullet_points": [
    "Key feature or benefit 1",
    "Key feature or benefit 2",
    "Key feature or benefit 3"
  ],
  "call_to_action": "compelling CTA",
  "shipping_notes": "shipping/pickup information if applicable"
}

Guidelines:
1. Be honest about condition and flaws
2. Highlight value propositions and benefits
3. Use clear, friendly language
4. Include relevant measurements/specs
5. Create urgency without being pushy
6. Optimize for search discoverability
7. Make it easy for buyers to say yes

Write copy that sells while being truthful and helpful."""

        return prompt

    def _parse_listing_response(self, response_text: str) -> Dict[str, Any]:
        """Parse listing response from Claude"""
        import json

        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                listing = json.loads(json_str)
                return listing
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            print(f"Error parsing listing response: {str(e)}")
            return {
                "title": "Item for Sale",
                "description": response_text[:500],
                "facebook_copy": response_text[:500],
                "short_description": "Item for sale",
                "hashtags": [],
                "keywords": [],
                "bullet_points": [],
                "call_to_action": "Message me if interested!",
                "shipping_notes": "Local pickup available"
            }

    def _mock_listing(
        self,
        item_name: str,
        description: str,
        condition: str,
        price: float
    ) -> Dict[str, Any]:
        """Generate mock listing for testing"""
        return {
            "title": f"{item_name} - {condition}",
            "description": f"{description}\n\nCondition: {condition}\nPrice: ${price:.2f}\n\nThis is mock listing copy. Set ANTHROPIC_API_KEY for AI-generated listings.",
            "facebook_copy": f"🔥 {item_name} for sale!\n\n{description[:200]}\n\nCondition: {condition}\n💰 ${price:.2f}\n\nLocal pickup available. Message me with questions!",
            "short_description": description[:100],
            "hashtags": ["forsale", "marketplace"],
            "keywords": item_name.lower().split(),
            "bullet_points": [
                f"Condition: {condition}",
                f"Priced to sell at ${price:.2f}",
                "Local pickup available"
            ],
            "call_to_action": "Message me to arrange pickup!",
            "shipping_notes": "Local pickup preferred"
        }
