# Integrating with nessie (or any automation)

This tool is a small HTTP service. Your automation stack (nessie / openclaw / Hermes)
sends it photos and gets back a finished, paste-ready Facebook Marketplace listing.

## The one endpoint you need

```
POST http://localhost:8000/api/analyze
Content-Type: multipart/form-data
Header (optional): X-API-Key: <APP_API_KEY>
```

**Form fields**
| field       | required | notes                                             |
|-------------|----------|---------------------------------------------------|
| `files`     | yes      | one or more image files (up to 10)                |
| `condition` | no       | `new` \| `like-new` \| `good` \| `fair` \| `poor` (default `good`) |
| `notes`     | no       | any extra context ("small scratch on back")       |

**Response (JSON)**
```json
{
  "success": true,
  "item_id": "3bfc53c0-...",
  "item_name": "Apple AirPods Pro (2nd Gen)",
  "category": "Electronics - Audio",
  "condition": "good",
  "price": 185,
  "quick_sale_price": 165,
  "title": "Apple AirPods Pro 2nd Gen - Noise Cancelling",
  "description": "full listing body ...",
  "ready_to_post": "TITLE: ...\nPRICE: $185\nCONDITION: good\n\n<full body>"
}
```

`ready_to_post` is the deliverable: one block your automation (or you) pastes straight
into Facebook Marketplace → **Create new listing → Item for sale**.

## Curl example
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "X-API-Key: your-key-if-set" \
  -F "files=@/path/to/photo1.jpg" \
  -F "files=@/path/to/photo2.jpg" \
  -F "condition=good" \
  -F "notes=barely used, comes with charger"
```

## Auth
- If `APP_API_KEY` is set in `.env`, every call must send `X-API-Key: <that value>`.
- If it's blank, the endpoint is open (fine for a local-only setup).

## How nessie should use it
1. nessie collects photos of an item.
2. nessie `POST`s them to `/api/analyze`.
3. nessie takes `ready_to_post` and either:
   - shows it to you to paste into Marketplace (reliable), **or**
   - drives the **dedicated** Facebook account to post it (opt-in, fragile — see below).

## About posting (read this)
Facebook has **no public API** to post personal Marketplace listings. There is no token
that makes `/api/post` publish for you. Options:
- **Paste (reliable):** use `ready_to_post`. ~10 seconds per item.
- **Browser automation (opt-in, risky):** set `ENABLE_BROWSER_POSTER=true` plus
  `FB_DEDICATED_EMAIL` / `FB_DEDICATED_PASSWORD` for a **throwaway account only**.
  It fills the listing form via a real browser. Against Facebook ToS; can get the
  account banned; selectors break when Facebook changes its UI. Never use your main
  account. See `backend/services/playwright_poster.py`.

## Running it as an always-on service
- Local: `cd backend && python main.py` (keep the window open), or run it under a
  process manager so nessie can always reach `http://localhost:8000`.
- Remote: deploy `backend/` to any host that runs Python (Render, Railway, a small VPS)
  and point nessie at that URL instead of localhost.
