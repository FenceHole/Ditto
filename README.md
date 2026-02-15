# 🤖 Marketplace Bot Analyzer

An AI-powered marketplace listing automation tool that analyzes photos of items you want to sell, determines optimal pricing, recommends the best platforms, generates compelling listing copy, and automates posting to Facebook Marketplace and other platforms.

## 🎯 Why This Bot is Different

**Real Market Data, Not Guesses:** Most pricing tools scrape current listings (seller asking prices). This bot uses **eBay SOLD listings** - actual completed sales showing what buyers really paid. This gives you accurate, data-driven pricing instead of hopeful guesses.

**All-in-One Automation:** Upload photos → Get identification, pricing, platform recommendations, and ready-to-post listings. Everything automated in one workflow.

## Features

✨ **AI Image Analysis**
- Upload photos and let Claude Vision API identify your items
- Automatic brand, model, and condition detection
- Feature extraction and detailed descriptions

💰 **Smart Pricing with Real eBay Sold Data**
- Uses **actual eBay SOLD listings** (completed sales, not asking prices!)
- Real market data from what buyers actually paid
- Statistical analysis of 50+ recent sold items
- Median, average, and percentile-based recommendations
- Condition-adjusted pricing
- Quick-sale vs. optimal price strategies
- Market demand estimation and turnover forecasting

🎯 **Marketplace Selection**
- Intelligent platform recommendations
- Match score based on item category and price
- Multi-platform support (Facebook, eBay, Mercari, etc.)

✍️ **Auto-Generated Listings**
- Compelling, SEO-optimized listing copy
- Platform-specific formatting
- Attention-grabbing titles and descriptions

📤 **Automated Posting**
- Direct posting to Facebook Marketplace
- Draft mode for review before posting
- Listing management and tracking

## Technology Stack

**Backend:**
- Python 3.9+
- FastAPI (REST API)
- Anthropic Claude API (Vision & Text)
- Database: JSON (development) / PostgreSQL / MongoDB (production)
- SQLAlchemy (async ORM for PostgreSQL)
- Motor (async driver for MongoDB)

**Frontend:**
- React 18
- Tailwind CSS
- Modern responsive design

## Quick Start

### Prerequisites

1. **Python 3.9 or higher**
2. **Anthropic API Key** (required) - Get one at [console.anthropic.com](https://console.anthropic.com)
3. **eBay Developer Account** (highly recommended for accurate pricing) - Sign up at [developer.ebay.com](https://developer.ebay.com)
4. **Facebook Access Token** (optional, for automated posting)
5. **Database** (optional for production):
   - PostgreSQL 12+ OR
   - MongoDB 4.4+

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
| `ANTHROPIC_API_KEY` | **Yes** | Your Anthropic API key for AI features |
| `EBAY_APP_ID` | **Recommended** | eBay Application ID (Client ID) for sold listings data |
| `EBAY_CERT_ID` | **Recommended** | eBay Certificate ID (Client Secret) |
| `EBAY_DEV_ID` | **Recommended** | eBay Developer ID |
| `EBAY_AUTH_TOKEN` | No | eBay User Auth Token (for posting, not needed for pricing) |
| `EBAY_SANDBOX` | No | Set to 'true' for testing (default: false) |
| `FACEBOOK_ACCESS_TOKEN` | No | Facebook token for automated posting |
| `FACEBOOK_PAGE_ID` | No | Your Facebook Page ID |
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

### Getting a Facebook Access Token

1. Create a Facebook App at [developers.facebook.com](https://developers.facebook.com)
2. Add the Marketplace API permissions
3. Generate a Page Access Token
4. Add the token to your `.env` file

## Project Structure

```
Ditto/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── models/
│   │   └── database.py        # Data models
│   ├── services/
│   │   ├── image_analyzer.py      # Claude Vision integration
│   │   ├── ebay_service.py        # eBay sold listings search
│   │   ├── price_estimator.py     # Pricing engine with eBay data
│   │   ├── marketplace_selector.py # Platform recommendations
│   │   ├── listing_generator.py   # Copy generation
│   │   ├── facebook_poster.py     # Facebook API integration
│   │   └── storage_manager.py     # File storage
│   ├── data/                  # JSON database (auto-created)
│   └── storage/               # Uploaded images (auto-created)
├── frontend/
│   └── marketplace-app.html   # React web interface
└── README.md
```

## Features in Detail

### Image Analysis
Uses Claude's Vision API to:
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

The project includes comprehensive integration tests:

```bash
cd backend
pytest tests/ -v
```

Run specific test categories:
```bash
# Run only fast tests
pytest tests/ -v -m "not slow"

# Run with coverage report
pytest tests/ -v --cov=. --cov-report=html
```

### Database

The application supports three database backends:

#### JSON Database (Default - Development)
No setup required. Data is stored in `backend/data/listings.json`.

#### PostgreSQL (Recommended for Production)

1. **Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

2. **Create Database**
```bash
sudo -u postgres psql
CREATE DATABASE marketplace_bot;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE marketplace_bot TO your_user;
\q
```

3. **Configure Environment**
```bash
# In .env file
DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost:5432/marketplace_bot
```

4. **Initialize Database**
The tables will be created automatically on first run.

5. **Migrate from JSON (Optional)**
```bash
cd backend
python scripts/migrate_database.py \
  --from json \
  --to postgres \
  --json-path ./data/listings.json \
  --target-url "postgresql+asyncpg://user:password@localhost:5432/marketplace_bot"
```

#### MongoDB (Alternative for Production)

1. **Install MongoDB**
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community
```

2. **Start MongoDB**
```bash
mongod --dbpath /path/to/data/directory
```

3. **Configure Environment**
```bash
# In .env file
DATABASE_URL=mongodb://localhost:27017
MONGO_DB_NAME=marketplace_bot
```

4. **Initialize Database**
Collections and indexes will be created automatically on first run.

5. **Migrate from JSON (Optional)**
```bash
cd backend
python scripts/migrate_database.py \
  --from json \
  --to mongodb \
  --json-path ./data/listings.json \
  --target-url "mongodb://localhost:27017"
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Copy `.env.example` to `.env`
- Add your Anthropic API key

### "Failed to analyze items"
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API key is valid

### "Facebook posting failed"
- Ensure you have a valid Facebook Access Token
- Check token permissions include Marketplace API
- Verify your Page ID is correct

### Images not uploading
- Check file size (10MB limit per file)
- Ensure images are valid formats (JPG, PNG, GIF, WebP)
- Check storage directory permissions

### Database Connection Errors

**PostgreSQL:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U your_user -d marketplace_bot -h localhost
```

**MongoDB:**
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Test connection
mongo mongodb://localhost:27017
```

**Common Issues:**
- Wrong credentials in DATABASE_URL
- Database server not running
- Firewall blocking connection
- Database doesn't exist (create it first)

### Migration Issues
- Ensure source JSON file exists and is valid
- Check target database is accessible
- Verify DATABASE_URL format is correct
- Check logs for specific error messages

### Performance Issues
- For large datasets, use PostgreSQL or MongoDB instead of JSON
- Increase database connection pool size in production
- Enable database query logging to identify slow queries

## Roadmap

- [x] PostgreSQL/MongoDB database support
- [x] Comprehensive integration testing
- [x] Database migration tools
- [x] Enhanced error handling and logging
- [ ] eBay API integration for posting
- [ ] Craigslist posting automation
- [ ] Mercari integration
- [ ] Bulk upload and batch processing
- [ ] Mobile app (React Native)
- [ ] Price tracking and repricing
- [ ] Automated listing renewals
- [ ] Multi-user support
- [ ] Analytics dashboard
- [ ] API rate limiting and caching
- [ ] Automated backup and recovery

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

- Built with [Claude](https://www.anthropic.com/claude) by Anthropic
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- UI built with [React](https://react.dev/) and [Tailwind CSS](https://tailwindcss.com/)

---

**Happy Selling! 🚀**
