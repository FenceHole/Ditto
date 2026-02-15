# Deployment Guide

This guide covers deploying the Marketplace Bot Analyzer to production environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Platform Deployments](#cloud-platform-deployments)
4. [Database Setup](#database-setup)
5. [Environment Variables](#environment-variables)
6. [Security Best Practices](#security-best-practices)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

- Python 3.9+
- PostgreSQL 12+ or MongoDB 4.4+
- API Keys (Anthropic, eBay, Facebook)
- Domain name (optional, for production)
- SSL certificate (recommended)

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/marketplace_bot
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - EBAY_APP_ID=${EBAY_APP_ID}
      - EBAY_CERT_ID=${EBAY_CERT_ID}
      - EBAY_DEV_ID=${EBAY_DEV_ID}
      - FACEBOOK_ACCESS_TOKEN=${FACEBOOK_ACCESS_TOKEN}
      - FACEBOOK_PAGE_ID=${FACEBOOK_PAGE_ID}
    depends_on:
      - db
    volumes:
      - ./backend/storage:/app/storage

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=marketplace_bot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend:/usr/share/nginx/html:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 3. Deploy

```bash
# Create .env file with your API keys
cp backend/.env.example .env
# Edit .env with your actual keys

# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Cloud Platform Deployments

### Heroku

1. **Create Heroku App**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
```

2. **Configure Environment Variables**
```bash
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set EBAY_APP_ID=your_app_id
heroku config:set EBAY_CERT_ID=your_cert_id
heroku config:set EBAY_DEV_ID=your_dev_id
heroku config:set FACEBOOK_ACCESS_TOKEN=your_token
heroku config:set FACEBOOK_PAGE_ID=your_page_id
```

3. **Create Procfile**
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

4. **Deploy**
```bash
git push heroku main
```

### Railway

1. **Create Project** at [railway.app](https://railway.app)

2. **Add PostgreSQL Database** from Railway dashboard

3. **Configure Environment Variables** in Railway dashboard

4. **Connect GitHub Repository** and deploy automatically

### AWS Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize EB Application**
```bash
eb init -p python-3.11 marketplace-bot
```

3. **Create Environment**
```bash
eb create marketplace-bot-env
```

4. **Configure Environment Variables**
```bash
eb setenv ANTHROPIC_API_KEY=your_key
eb setenv DATABASE_URL=your_postgres_url
```

5. **Deploy**
```bash
eb deploy
```

### DigitalOcean App Platform

1. **Create App** from DigitalOcean dashboard

2. **Connect GitHub Repository**

3. **Configure Build Settings**
- Build Command: `cd backend && pip install -r requirements.txt`
- Run Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8080`

4. **Add Database Component** (PostgreSQL or MongoDB)

5. **Set Environment Variables** in dashboard

6. **Deploy**

## Database Setup

### PostgreSQL Production Setup

```bash
# Create production database
sudo -u postgres psql
CREATE DATABASE marketplace_bot;
CREATE USER prod_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE marketplace_bot TO prod_user;

# Configure connection pooling (optional but recommended)
# Edit postgresql.conf:
max_connections = 100
shared_buffers = 256MB
```

### MongoDB Production Setup

```bash
# Start MongoDB with authentication
mongod --auth --port 27017

# Create admin user
mongo
use admin
db.createUser({
  user: "admin",
  pwd: "secure_password",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

# Create application user
use marketplace_bot
db.createUser({
  user: "prod_user",
  pwd: "secure_password",
  roles: [ { role: "readWrite", db: "marketplace_bot" } ]
})
```

## Environment Variables

### Required
- `ANTHROPIC_API_KEY` - Your Anthropic API key

### Recommended
- `EBAY_APP_ID` - eBay Application ID
- `EBAY_CERT_ID` - eBay Certificate ID  
- `EBAY_DEV_ID` - eBay Developer ID

### Optional
- `FACEBOOK_ACCESS_TOKEN` - Facebook API token
- `FACEBOOK_PAGE_ID` - Facebook Page ID
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)
- `DATABASE_URL` - Database connection string

### Security
- `SECRET_KEY` - Application secret (generate with `openssl rand -hex 32`)

## Security Best Practices

### 1. API Keys
- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate keys regularly
- Use separate keys for development/production

### 2. Database Security
- Use strong passwords
- Enable SSL/TLS for database connections
- Restrict database access by IP
- Regular backups

### 3. Application Security
- Enable HTTPS/SSL in production
- Configure CORS properly (don't use `allow_origins=["*"]` in production)
- Implement rate limiting
- Add authentication for sensitive endpoints
- Keep dependencies updated

### 4. File Storage
- Validate uploaded files
- Implement file size limits
- Scan uploads for malware
- Use cloud storage (S3, GCS) for production

### Example Production CORS Configuration

```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Monitoring and Maintenance

### Logging

Configure structured logging for production:

```python
# Set LOG_LEVEL environment variable
LOG_LEVEL=INFO  # or WARNING for less verbose logging
```

### Health Checks

The application includes a health check endpoint:
```
GET /
```

Configure your load balancer/platform to monitor this endpoint.

### Monitoring Tools

Recommended:
- **Sentry** - Error tracking
- **New Relic** - Application performance monitoring
- **Datadog** - Infrastructure monitoring
- **Prometheus + Grafana** - Metrics and dashboards

### Database Backups

**PostgreSQL:**
```bash
# Automated daily backup
pg_dump -h localhost -U prod_user marketplace_bot > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h localhost -U prod_user marketplace_bot < backup_20240101.sql
```

**MongoDB:**
```bash
# Backup
mongodump --uri="mongodb://prod_user:password@localhost:27017/marketplace_bot"

# Restore
mongorestore --uri="mongodb://prod_user:password@localhost:27017/marketplace_bot" dump/
```

### Performance Optimization

1. **Database Connection Pooling** - Already configured in PostgreSQL adapter
2. **Caching** - Consider adding Redis for frequently accessed data
3. **CDN** - Use CloudFlare or similar for static assets
4. **Compression** - Enable gzip compression in nginx/load balancer
5. **Async Operations** - All I/O operations are already async

### Scaling

**Horizontal Scaling:**
- Run multiple backend instances behind a load balancer
- Use shared database (PostgreSQL/MongoDB)
- Store uploaded files in shared storage (S3, GCS)

**Vertical Scaling:**
- Increase server resources (CPU, RAM)
- Tune database parameters
- Optimize database queries

## Troubleshooting Production Issues

### Application Won't Start
```bash
# Check logs
docker-compose logs backend
# or
heroku logs --tail

# Verify environment variables
printenv | grep -E 'ANTHROPIC|DATABASE'
```

### Database Connection Issues
```bash
# Test database connectivity
psql -h hostname -U username -d database_name

# Check connection string format
# PostgreSQL: postgresql+asyncpg://user:pass@host:port/dbname
# MongoDB: mongodb://user:pass@host:port
```

### High Memory Usage
- Check database query performance
- Monitor API response times
- Consider implementing caching
- Review file upload handling

### Slow API Responses
- Enable query logging
- Check external API timeouts (eBay, Facebook)
- Monitor database performance
- Consider adding Redis cache

## Support

For deployment issues:
1. Check application logs
2. Verify all environment variables are set
3. Test database connectivity
4. Review platform-specific documentation
5. Open an issue on GitHub

---

**Need help?** Open an issue on GitHub or contact support.
