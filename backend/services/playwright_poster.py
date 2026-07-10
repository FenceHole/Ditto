"""
OPTIONAL Browser Poster — Facebook Marketplace (DEDICATED ACCOUNT ONLY)

⚠️  READ THIS BEFORE ENABLING ⚠️
- Facebook has no official API for posting personal Marketplace listings, so this
  drives a real browser (Playwright) that logs in and fills the "Create listing"
  form. This is against Facebook's Terms of Service.
- Automated activity can get an account BANNED. NEVER point this at your main /
  business / monetized account. Use a throwaway account dedicated to Marketplace.
- Facebook changes its page layout often, so selectors here WILL break over time.
  Treat this as best-effort convenience, not a dependable robot. The reliable path
  is the paste-ready listing from /api/analyze.

This module only runs when ENABLE_BROWSER_POSTER=true AND credentials are set:
    ENABLE_BROWSER_POSTER=true
    FB_DEDICATED_EMAIL=...
    FB_DEDICATED_PASSWORD=...

Requires:  pip install playwright  &&  playwright install chromium
(In this hosting environment Chromium is preinstalled at /opt/pw-browsers/chromium.)
"""

import os
from typing import Any, Dict


class PlaywrightPoster:
    """Best-effort Marketplace poster for a dedicated account. Opt-in and fragile."""

    def __init__(self):
        self.email = os.getenv("FB_DEDICATED_EMAIL")
        self.password = os.getenv("FB_DEDICATED_PASSWORD")
        self.headless = os.getenv("BROWSER_POSTER_HEADLESS", "true").lower() == "true"
        # Allow a preinstalled Chromium path (set PLAYWRIGHT_CHROMIUM_PATH to override).
        self.executable_path = os.getenv("PLAYWRIGHT_CHROMIUM_PATH")

    async def post_item(self, item: Any) -> Dict[str, Any]:
        """
        Attempt to create a Marketplace listing for `item` on the dedicated account.
        Returns a status dict; never raises so it can't crash the API request.
        """
        if not self.email or not self.password:
            return {
                "status": "skipped",
                "message": "Set FB_DEDICATED_EMAIL and FB_DEDICATED_PASSWORD to enable.",
            }

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return {
                "status": "error",
                "message": "playwright not installed. Run: pip install playwright "
                           "&& playwright install chromium",
            }

        title = item.listing_copy.get("title", item.item_name)
        price = item.pricing_data.get("recommended_price", 0)
        try:
            price_str = str(int(float(price)))
        except (TypeError, ValueError):
            price_str = "0"
        description = item.listing_copy.get(
            "facebook_copy", item.listing_copy.get("description", item.description)
        )

        try:
            async with async_playwright() as p:
                launch_kwargs = {"headless": self.headless}
                if self.executable_path:
                    launch_kwargs["executable_path"] = self.executable_path
                browser = await p.chromium.launch(**launch_kwargs)
                context = await browser.new_context()
                page = await context.new_page()

                # 1) Log in
                await page.goto("https://www.facebook.com/login", wait_until="domcontentloaded")
                await page.fill("#email", self.email)
                await page.fill("#pass", self.password)
                await page.click("button[name='login']")
                await page.wait_for_load_state("networkidle")

                # 2) Open the "Item for sale" create form
                await page.goto(
                    "https://www.facebook.com/marketplace/create/item",
                    wait_until="domcontentloaded",
                )
                await page.wait_for_load_state("networkidle")

                # 3) Upload photos
                try:
                    file_input = await page.query_selector("input[type='file']")
                    if file_input and item.image_paths:
                        await file_input.set_input_files(item.image_paths[:10])
                except Exception:
                    pass  # non-fatal; user can add photos manually

                # 4) Fill fields. Facebook uses aria-labels that shift over time —
                #    these are best-effort and may need updating when FB changes its UI.
                await self._fill_by_label(page, "Title", title)
                await self._fill_by_label(page, "Price", price_str)
                await self._fill_by_label(page, "Description", description)

                # Intentionally NOT auto-clicking "Publish": leave the filled draft for a
                # human to review and submit. Set BROWSER_POSTER_AUTOPUBLISH=true to publish.
                published = False
                if os.getenv("BROWSER_POSTER_AUTOPUBLISH", "false").lower() == "true":
                    try:
                        await page.click("div[aria-label='Publish']", timeout=5000)
                        published = True
                    except Exception:
                        published = False

                await browser.close()

                return {
                    "status": "draft_filled" if not published else "published",
                    "message": (
                        "Listing form filled on the dedicated account. Review and click "
                        "Publish." if not published else "Listing published (auto)."
                    ),
                }
        except Exception as e:
            return {"status": "error", "message": f"Browser poster failed: {e}"}

    async def _fill_by_label(self, page, label: str, value: str):
        """Try a few selector strategies to fill a labelled field. Best-effort."""
        selectors = [
            f"input[aria-label='{label}']",
            f"textarea[aria-label='{label}']",
            f"label:has-text('{label}') input",
            f"label:has-text('{label}') textarea",
        ]
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.fill(value)
                    return
            except Exception:
                continue
