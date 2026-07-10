"""
Image Analyzer Service
Uses Google Gemini Vision API to identify items from photos (FREE!)
"""

import base64
import os
from typing import List, Dict, Any, Optional
import json
import requests


class ImageAnalyzer:
    """Analyzes item images using Google Gemini Vision API (FREE)"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not set. Image analysis will use mock data.")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    async def analyze_images(
        self,
        image_paths: List[str],
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze images to identify item, condition, and features using Gemini Vision (FREE)

        Args:
            image_paths: List of paths to image files
            additional_context: Optional additional context from user

        Returns:
            Dictionary containing item identification and analysis
        """
        if not self.api_key:
            # Fallback for testing without API key
            return self._mock_analysis(image_paths)

        try:
            # Prepare images for Gemini
            parts = []

            # Add the text prompt first
            prompt = self._build_analysis_prompt(additional_context)
            parts.append({"text": prompt})

            # Add images (limit to 5)
            for img_path in image_paths[:5]:
                with open(img_path, "rb") as img_file:
                    image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")

                    # Detect image type
                    ext = img_path.lower().split('.')[-1]
                    mime_type_map = {
                        'jpg': 'image/jpeg',
                        'jpeg': 'image/jpeg',
                        'png': 'image/png',
                        'gif': 'image/gif',
                        'webp': 'image/webp'
                    }
                    mime_type = mime_type_map.get(ext, 'image/jpeg')

                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_data
                        }
                    })

            # Call Gemini API
            payload = {
                "contents": [{
                    "parts": parts
                }],
                "generationConfig": {
                    "temperature": 0.4,
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

            # Extract text from Gemini response
            response_text = result['candidates'][0]['content']['parts'][0]['text']

            # Extract JSON from response
            analysis = self._parse_analysis_response(response_text)

            return analysis

        except Exception as e:
            print(f"Error analyzing images: {str(e)}")
            raise Exception(f"Image analysis failed: {str(e)}")

    def _build_analysis_prompt(self, additional_context: Optional[str] = None) -> str:
        """Build the analysis prompt for Claude"""
        prompt = """Analyze the provided images and identify the item for marketplace listing.

Please provide a detailed JSON response with the following information:

{
  "identified": true/false,
  "item_name": "specific product name",
  "category": "main category (e.g., Electronics, Furniture, Clothing, Sports, etc.)",
  "subcategory": "more specific category",
  "brand": "brand name if visible/identifiable",
  "model": "model number/name if identifiable",
  "description": "detailed description of the item (2-3 sentences)",
  "features": ["list", "of", "key", "features", "and", "characteristics"],
  "attributes": {
    "color": "primary color",
    "size": "size if applicable",
    "material": "material if identifiable",
    "age": "estimated age/era"
  },
  "condition_notes": "visible wear, damage, or condition indicators",
  "keywords": ["searchable", "keywords", "for", "listing"],
  "confidence": "high/medium/low"
}

Focus on:
1. Accurate identification of the product
2. Brand and model if visible
3. Key selling features
4. Condition indicators (scratches, wear, etc.)
5. Unique characteristics that would help pricing

Be specific and detailed. If you can't identify something with confidence, indicate lower confidence."""

        if additional_context:
            prompt += f"\n\nAdditional context from user: {additional_context}"

        return prompt

    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response into structured data"""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                return analysis
            else:
                # If no JSON found, create structured response from text
                return {
                    "identified": True,
                    "item_name": "Unknown Item",
                    "category": "General",
                    "description": response_text[:500],
                    "features": [],
                    "confidence": "low"
                }

        except json.JSONDecodeError:
            print(f"Failed to parse JSON from response: {response_text[:200]}")
            return {
                "identified": False,
                "item_name": "Unknown",
                "category": "General",
                "description": "Could not analyze item",
                "features": [],
                "confidence": "low"
            }

    def _mock_analysis(self, image_paths: List[str]) -> Dict[str, Any]:
        """Mock analysis for testing without API key"""
        return {
            "identified": True,
            "item_name": "Sample Item (Mock Data)",
            "category": "Electronics",
            "subcategory": "Consumer Electronics",
            "brand": "Generic",
            "model": "Model X",
            "description": "This is a mock analysis. Set GEMINI_API_KEY to enable real image analysis.",
            "features": [
                "Feature 1",
                "Feature 2",
                "Feature 3"
            ],
            "attributes": {
                "color": "Black",
                "size": "Medium",
                "material": "Plastic",
                "age": "Recent"
            },
            "condition_notes": "Appears to be in good condition",
            "keywords": ["sample", "item", "test"],
            "confidence": "low"
        }
