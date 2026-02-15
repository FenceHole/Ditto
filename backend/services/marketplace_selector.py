"""
Marketplace Selector Service
Recommends optimal marketplaces based on item characteristics
"""

from typing import Dict, Any, List


class MarketplaceSelector:
    """Selects optimal marketplaces for item listing"""

    def __init__(self):
        # Marketplace characteristics and best-fit categories
        self.marketplace_profiles = {
            "facebook": {
                "name": "Facebook Marketplace",
                "best_for": ["Furniture", "Home Goods", "Baby Items", "Vehicles", "Local Services"],
                "price_range": (5, 10000),
                "local_focus": True,
                "fees": "Free for local sales",
                "audience": "Local community buyers",
                "speed": "Fast (1-7 days typical)"
            },
            "craigslist": {
                "name": "Craigslist",
                "best_for": ["Furniture", "Vehicles", "Electronics", "Housing", "Services"],
                "price_range": (0, 50000),
                "local_focus": True,
                "fees": "Free for most categories",
                "audience": "Local buyers, often looking for deals",
                "speed": "Fast (1-5 days typical)"
            },
            "ebay": {
                "name": "eBay",
                "best_for": ["Collectibles", "Electronics", "Fashion", "Antiques", "Rare Items"],
                "price_range": (1, 100000),
                "local_focus": False,
                "fees": "~13% total fees",
                "audience": "Global buyers, collectors",
                "speed": "Medium (3-14 days typical)"
            },
            "mercari": {
                "name": "Mercari",
                "best_for": ["Fashion", "Electronics", "Beauty", "Toys", "Collectibles"],
                "price_range": (3, 2000),
                "local_focus": False,
                "fees": "10% selling fee + shipping",
                "audience": "Young adults, bargain hunters",
                "speed": "Medium (2-10 days typical)"
            },
            "offerup": {
                "name": "OfferUp",
                "best_for": ["Furniture", "Electronics", "Home Goods", "Vehicles"],
                "price_range": (5, 10000),
                "local_focus": True,
                "fees": "Free for local, fees for shipping",
                "audience": "Local buyers with ratings system",
                "speed": "Fast (1-7 days typical)"
            },
            "poshmark": {
                "name": "Poshmark",
                "best_for": ["Fashion", "Shoes", "Accessories", "Designer Items"],
                "price_range": (5, 5000),
                "local_focus": False,
                "fees": "20% for items over $15",
                "audience": "Fashion-focused buyers",
                "speed": "Medium (3-14 days typical)"
            },
            "depop": {
                "name": "Depop",
                "best_for": ["Vintage Fashion", "Streetwear", "Y2K", "Unique Clothing"],
                "price_range": (5, 1000),
                "local_focus": False,
                "fees": "10% selling fee",
                "audience": "Gen Z fashion enthusiasts",
                "speed": "Medium (2-14 days typical)"
            }
        }

    async def select_marketplaces(
        self,
        category: str,
        estimated_price: float,
        item_type: str,
        ebay_sold_data: Dict[str, Any] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Select optimal marketplaces for the item

        Args:
            category: Item category
            estimated_price: Estimated price
            item_type: Specific item type
            ebay_sold_data: eBay sold listings data (boosts eBay score if available)

        Returns:
            List of recommended marketplaces with scores
        """
        recommendations = []

        for marketplace_id, profile in self.marketplace_profiles.items():
            score = self._calculate_marketplace_score(
                profile, category, estimated_price, item_type
            )

            # Boost eBay score if we have good sold data
            if marketplace_id == "ebay" and ebay_sold_data and ebay_sold_data.get('success'):
                sold_count = ebay_sold_data.get('sold_count', 0)
                if sold_count > 20:
                    score += 15  # Strong eBay market
                    reasoning_extra = f" {sold_count} recent sales found on eBay - proven market!"
                elif sold_count > 10:
                    score += 10  # Good eBay market
                    reasoning_extra = f" {sold_count} sales found on eBay - active market"
                elif sold_count > 5:
                    score += 5  # Some eBay activity
                    reasoning_extra = f" {sold_count} sales found on eBay"
                else:
                    reasoning_extra = ""
            else:
                reasoning_extra = ""

            if score > 0:
                recommendations.append({
                    "marketplace": marketplace_id,
                    "name": profile["name"],
                    "score": score,
                    "priority": self._get_priority_level(score),
                    "reasoning": self._generate_reasoning(profile, category, score) + reasoning_extra,
                    "fees": profile["fees"],
                    "estimated_speed": profile["speed"],
                    "audience": profile["audience"]
                })

        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        # Return top 4 recommendations (include eBay if it's relevant)
        return recommendations[:4]

    def _calculate_marketplace_score(
        self,
        profile: Dict[str, Any],
        category: str,
        price: float,
        item_type: str
    ) -> float:
        """Calculate fit score for a marketplace (0-100)"""
        score = 50.0  # Base score

        # Category match
        category_lower = category.lower()
        for best_category in profile["best_for"]:
            if best_category.lower() in category_lower or category_lower in best_category.lower():
                score += 30
                break
        else:
            # Partial match
            for best_category in profile["best_for"]:
                if any(word in best_category.lower() for word in category_lower.split()):
                    score += 15
                    break

        # Price range match
        min_price, max_price = profile["price_range"]
        if min_price <= price <= max_price:
            score += 15
        elif price < min_price:
            score -= 20
        elif price > max_price:
            score -= 10

        # Bonus for Facebook (primary marketplace - always relevant)
        if profile["name"] == "Facebook Marketplace":
            score += 10

        return max(0, min(100, score))

    def _get_priority_level(self, score: float) -> str:
        """Convert score to priority level"""
        if score >= 80:
            return "high"
        elif score >= 60:
            return "medium"
        else:
            return "low"

    def _generate_reasoning(
        self,
        profile: Dict[str, Any],
        category: str,
        score: float
    ) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasons = []

        if score >= 80:
            reasons.append(f"Excellent match for {category}")
        elif score >= 60:
            reasons.append(f"Good fit for {category}")
        else:
            reasons.append(f"Possible option for {category}")

        if profile["local_focus"]:
            reasons.append("Great for local pickup")
        else:
            reasons.append("Nationwide/global reach")

        reasons.append(f"Typical speed: {profile['speed']}")

        return ". ".join(reasons)
