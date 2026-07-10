"""
Listing Generator Service
Creates compelling marketplace listing copy using Gemini (FREE!)
"""

import os
from typing import List, Dict, Any, Optional
import requests


class ListingGenerator:
    """Generates optimized listing copy for marketplaces using Gemini (FREE)"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

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
        Generate compelling listing copy using Gemini (FREE)

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
        if not self.api_key:
            return self._mock_listing(item_name, description, condition, price)

        try:
            prompt = self._build_listing_prompt(
                item_name, description, condition, price, features, additional_notes
            )

            # Call Gemini API
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048,
                }
            }

            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json=payload
            )

            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.text}")

            result = response.json()
            response_text = result['candidates'][0]['content']['parts'][0]['text']

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
            "description": f"{description}\n\nCondition: {condition}\nPrice: ${price:.2f}\n\nThis is mock listing copy. Set GEMINI_API_KEY for AI-generated listings.",
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
