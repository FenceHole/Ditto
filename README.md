# 🤖 Marketplace Bot Analyzer

Give it photos of something you want to sell. It identifies the item, sets a smart price,
and writes the complete Facebook Marketplace listing. You paste the finished listing into
Facebook and post. Built to plug into your own automation (see `INTEGRATION.md`).

> **Honest note on posting:** Facebook has **no public API** for posting personal Marketplace
> listings, so nothing can truly "auto-post" to your Marketplace safely. This app does the hard
> part (identify → price → write the listing) and hands you a **paste-ready** block. An optional,
> opt-in browser robot exists for a **dedicated throwaway account only** (see `SETUP.md`) — it's
> against Facebook's ToS and can get an account banned, so never use your main account.

## Features

✨ **AI Image Analysis** (free — Google Gemini)
- Upload photos and let Gemini Vision identify your items
- Brand, model, and condition detection
- Feature extraction and detailed descriptions

💰 **Smart Pricing**
- Condition-adjusted price plus a quick-sale price for fast turnover
- Optional eBay **sold-listings** research (off by default) for real "what buyers paid" data

✍️ **Finished, Paste-Ready Listings**
- Title, price, and a compelling description
- One `ready_to_post` block to paste straight into Marketplace

🔌 **Automation-Friendly**
- One clean endpoint (`POST /api/analyze`) your nessie/openclaw/Hermes setup can call

## Technology Stack

**Backend:**
- Python 3.9+
- FastAPI (REST API)
- Google Gemini API (free — Vision & Text)
- JSON-based database (upgradeable to PostgreSQL/MongoDB)

**Frontend:**
- React 18 + Tailwind CSS (single-file `frontend/marketplace-app.html`)

## Quick Start

### Prerequisites

1. **Python 3.9 or higher**
2. **Free Google Gemini API key** (required) — get one at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
3. **eBay Developer Account** (optional, for sold-price research) — [developer.ebay.com](https://developer.ebay.com)
4. **A dedicated Facebook account** (optional, only if you enable the browser poster)

See **QUICKSTART.md** for the simplest path, or **INTEGRATION.md** to wire it into nessie.

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Ditto
```

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
# Required for AI features
ANTHROPIC_API_KEY=your_key_here

# Highly recommended - for real pricing data
EBAY_APP_ID=your_ebay_app_id
EBAY_CERT_ID=your_ebay_cert_id
EBAY_DEV_ID=your_ebay_dev_id

# Optional - for automated Facebook posting
FACEBOOK_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=your_page_id
```

4. **Start the backend server**
```bash
python main.py
```

The API will be running at `http://localhost:8000`

5. **Open the frontend**

Open `frontend/marketplace-app.html` in your web browser, or serve it with a simple HTTP server:

```bash
cd frontend
python -m http.server 3000
```

Then visit `http://localhost:3000/marketplace-app.html`

## Usage

### 1. Upload Photos

- Click or drag-and-drop up to 10 photos of your item
- Select the item condition (New, Like-New, Good, Fair, Poor)
- Add any additional notes about the item (optional)

### 2. Analyze

- Click "Analyze & Generate Listing"
- The AI will:
  - Identify the item from your photos
  - Determine brand, model, and features
  - **Search eBay sold listings** for real market pricing (actual sales!)
  - Research market prices using AI + sold data
  - Recommend optimal selling platforms based on sales velocity
  - Generate compelling listing copy

### 3. Review Results

Review the generated:
- **Item identification** - Name, category, brand, features
- **Pricing recommendations** - Based on real eBay sold data:
  - Recommended price (median of actual sales)
  - Quick-sale price (25th percentile for fast turnover)
  - Market demand and sales velocity
  - Price range from actual sold items
- **Marketplace suggestions** - Best platforms ranked by match score and sales history
- **Listing copy** - Title, description, and platform-specific formatting

### 4. Post to Marketplaces

- Click "Post to Facebook Marketplace" to create your listing
- Or manually copy the generated text to other platforms

### 5. Track History

- View all your past listings
- See posting status and prices
- Manage your inventory

## API Endpoints

### POST /api/upload
Upload photos for analysis
- **Body:** FormData with images, condition, notes
- **Returns:** Complete analysis with pricing and listing copy

### POST /api/post
Post item to marketplace
- **Body:** `{item_id, marketplaces, auto_post}`
- **Returns:** Posting status and URLs

### GET /api/listings
Get listing history
- **Query:** `status`, `limit`, `offset`
- **Returns:** Array of listings

### GET /api/listings/{item_id}
Get specific listing

### PUT /api/listings/{item_id}
Update listing

### DELETE /api/listings/{item_id}
Delete listing

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | **Yes** | Your free Google Gemini API key (powers analysis + listing writing) |
| `APP_API_KEY` | No | If set, callers must send `X-API-Key` header (for nessie/automation) |
| `EBAY_APP_ID` | No | eBay Application ID (Client ID) for optional sold-listings pricing |
| `EBAY_CERT_ID` | No | eBay Certificate ID (Client Secret) |
| `EBAY_DEV_ID` | No | eBay Developer ID |
| `ENABLE_BROWSER_POSTER` | No | `true` to enable the optional browser poster (dedicated account only) |
| `FB_DEDICATED_EMAIL` | No | Dedicated (throwaway) Facebook account email for the browser poster |
| `FB_DEDICATED_PASSWORD` | No | Dedicated account password for the browser poster |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 8000) |
| `UPLOAD_DIR` | No | Upload directory path |

### Getting eBay API Credentials (Recommended for Accurate Pricing)

**Why eBay?** The bot uses eBay's **sold listings** (actual completed sales) to determine accurate pricing. Unlike other sources that show asking prices (seller hopes), eBay sold data shows what buyers actually paid - real market value!

1. Go to [developer.ebay.com](https://developer.ebay.com) and create an account
2. Create an Application:
   - Click "Create Application Key"
   - Choose "Production" environment
   - Fill in application details
3. Get your credentials:
   - **App ID (Client ID)** - Your application's identifier
   - **Cert ID (Client Secret)** - Your application's secret
   - **Dev ID** - Your developer ID (from account page)
4. Add credentials to your `.env` file:
   ```
   EBAY_APP_ID=YourAppI-YourApp-PRD-abcdef123
   EBAY_CERT_ID=PRD-abcdef123456
   EBAY_DEV_ID=your-dev-id
   ```

**Note:** You only need the Finding API access (which is free) for pricing research. You don't need special permissions or user tokens unless you want to post to eBay (not currently supported).

### Posting to Facebook

There is no Facebook access token that posts to personal Marketplace — Facebook doesn't
offer one. Post by pasting the `ready_to_post` block, or enable the optional browser poster
for a dedicated account (see **SETUP.md**).

## Project Structure

```
Ditto/
├── backend/
│   ├── main.py                 # FastAPI app (/api/analyze, /api/post, listings)
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── models/
│   │   └── database.py        # Data models
│   ├── services/
│   │   ├── image_analyzer.py      # Gemini Vision item identification
│   │   ├── ebay_service.py        # Optional eBay sold-listings search
│   │   ├── price_estimator.py     # Pricing engine (Gemini + optional eBay)
│   │   ├── marketplace_selector.py # Platform ranking
│   │   ├── listing_generator.py   # Gemini listing copy
│   │   ├── facebook_poster.py     # Paste-ready formatter (no fake API calls)
│   │   ├── playwright_poster.py   # Optional browser poster (dedicated acct, opt-in)
│   │   └── storage_manager.py     # File storage
│   ├── data/                  # JSON database (auto-created)
│   └── storage/               # Uploaded images (auto-created)
├── frontend/
│   └── marketplace-app.html   # React web interface
├── INTEGRATION.md             # How nessie/automation calls the service
└── README.md
```

## Features in Detail

### Image Analysis
Uses Google Gemini Vision to:
- Identify products from photos
- Detect brands and models
- Extract key features
- Assess visual condition
- Generate detailed descriptions

### Price Estimation (eBay Sold Data Integration)
The pricing engine searches eBay's **completed/sold listings** API to find actual sales:
- Searches up to 50 recent sold items matching your product
- Analyzes real prices buyers paid (not seller asking prices)
- Calculates statistical pricing:
  - **Median price** - Most reliable center point
  - **25th percentile** - For quick sales (priced to move)
  - **75th percentile** - Upper market range
  - **Average, min, max** - Full price spectrum
- Market activity analysis:
  - Sales velocity (how many sold in last 30 days)
  - Market demand (high/medium/low)
  - Estimated days to sell
- AI-enhanced recommendations using sold data + item condition
- Fallback to AI estimates if eBay data unavailable
- Seasonal demand factors
- Brand value impact
- Quick-sale vs. maximum value tradeoffs

### Marketplace Selection
Recommends platforms based on:
- Item category fit
- Price range compatibility
- Local vs. shipping options
- Typical turnover speed
- Fee structures
- Target audience

Supported marketplaces:
- Facebook Marketplace (integrated)
- Craigslist
- eBay
- Mercari
- OfferUp
- Poshmark
- Depop

### Listing Generation
Creates:
- SEO-optimized titles
- Compelling descriptions
- Platform-specific copy
- Bullet-point features
- Call-to-action phrases
- Shipping/pickup notes

## Development

### Running in Development Mode

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
pytest tests/
```

### Database

Currently uses a simple JSON file database for development. For production, migrate to PostgreSQL or MongoDB:

```python
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost/marketplace_bot
```

## Troubleshooting

### "GEMINI_API_KEY not set" (results look like mock/sample data)
- Rename `backend/.env.simple` to `backend/.env`
- Add your free key: `GEMINI_API_KEY=...` (from https://aistudio.google.com/app/apikey)
- Restart the server

### "Failed to analyze items"
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify your Gemini key is valid

### "Nothing auto-posts to Facebook"
- Expected — Facebook has no API for personal Marketplace posting.
- Paste the `ready_to_post` block into Marketplace, or enable the optional browser
  poster for a dedicated account (see SETUP.md).

### Images not uploading
- Check file size (10MB limit per file)
- Ensure images are valid formats (JPG, PNG, GIF, WebP)
- Check storage directory permissions

## Roadmap

- [ ] eBay API integration
- [ ] Craigslist posting automation
- [ ] Mercari integration
- [ ] Bulk upload and batch processing
- [ ] PostgreSQL/MongoDB migration
- [ ] Mobile app (React Native)
- [ ] Price tracking and repricing
- [ ] Automated listing renewals
- [ ] Multi-user support
- [ ] Analytics dashboard

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `http://localhost:8000/docs`

## Acknowledgments

- AI by [Google Gemini](https://ai.google.dev/) (free tier)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- UI built with [React](https://react.dev/) and [Tailwind CSS](https://tailwindcss.com/)

---

**Happy Selling! 🚀**
