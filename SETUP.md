# Setup & How Posting Really Works

## The 2-minute version
1. Get a **free** Gemini key: https://aistudio.google.com/app/apikey
2. Rename `backend/.env.simple` → `backend/.env`, paste the key after `GEMINI_API_KEY=`
3. Run `START.bat` (Windows) or `START.sh` (Mac)
4. Open http://localhost:8000/docs, upload photos, copy the listing, paste into Facebook.

That's the whole thing. No paid API, no Facebook developer account needed.

---

## Why there's no "auto-post to Facebook" button

Facebook **does not offer an API** for posting personal Marketplace listings. Any tool that
claims to auto-post to your Marketplace via an official API is mistaken — that door is closed.
(This is almost certainly why an earlier version felt "broken": it was calling Facebook
endpoints that don't work for personal selling.)

So this app is built the honest way:
- **The app does the hard 95%:** identify the item, price it using market knowledge, and
  write the full listing (title, price, description).
- **You do the easy 5%:** paste it into Facebook Marketplace and hit Post (~10 seconds).

## Optional: the browser-robot poster (advanced, risky)

If you want closer to hands-off, there's an **opt-in** poster that drives a real web browser
to fill out the Marketplace form for you.

**Rules of the road:**
- Use a **dedicated, throwaway Facebook account** — NEVER your main / business / monetized
  account. Browser automation is against Facebook's Terms and **can get an account banned.**
- It's **fragile**: Facebook changes its page layout often, which breaks the auto-filler.
- Brand-new accounts sometimes can't use Marketplace right away.

**To enable it**, in `backend/.env`:
```
ENABLE_BROWSER_POSTER=true
FB_DEDICATED_EMAIL=your_throwaway_account_email
FB_DEDICATED_PASSWORD=your_throwaway_account_password
```
and install the browser tool once:
```
pip install playwright
playwright install chromium
```
By default it **fills a draft and stops** so you can review before publishing. It only ever
touches the dedicated account you configured above.

## Hooking it into nessie
See **INTEGRATION.md** — one endpoint, photos in, finished listing out.
