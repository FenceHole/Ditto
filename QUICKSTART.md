# ⚡ Quickstart

**What this does:** You give it photos of something you want to sell. It figures out what
the item is, sets a smart price, and writes the whole Facebook Marketplace listing for you.
You paste that into Facebook and hit post.

**What it costs:** $0. It uses Google's **free** Gemini AI.

---

## Step 1 — Get your free Gemini key (2 minutes)

1. Go to: **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **Create API key**
4. **Copy** the key it shows you

No credit card. No charge.

## Step 2 — Put the key in the settings file (1 minute)

1. Open the `backend` folder
2. Find the file **`.env.simple`** and rename it to **`.env`**
3. Open `.env` and paste your key after `GEMINI_API_KEY=`
   ```
   GEMINI_API_KEY=paste_your_key_here
   ```
4. Save

## Step 3 — Start it

- **Windows:** double-click **`START.bat`**
- **Mac:** open `START.sh`

Wait until it says **"started successfully."**

## Step 4 — Use it

Open your browser to **http://localhost:8000/docs** (or open
`frontend/marketplace-app.html`), upload photos, and it gives you a finished listing with a
**Copy** button. Paste that into Facebook Marketplace → *Create new listing → Item for sale*.

---

## About posting to Facebook — please read

There is **no safe way to make an app auto-post** to Facebook Marketplace — Facebook blocks
it. So this app does the hard part (finding the item, pricing, writing the listing) and you
do the easy 10-second part (paste + post).

If you *really* want hands-off posting, there's an **optional** browser robot you can turn on
for a **throwaway/dedicated** Facebook account only — never your main one, because it can get
an account banned. See **SETUP.md**.

## Hooking it into your own automation (nessie)

See **INTEGRATION.md** — it's one endpoint (`/api/analyze`): send photos, get back a finished
listing. Your nessie/openclaw/Hermes setup can call it and handle posting however it does.
