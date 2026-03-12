# LLM Maps - AI-Powered Place Finder

A full-stack application that combines a local LLM with Google Maps API to provide intelligent place recommendations.

## 📋 Project Overview

This application allows users to search for places (restaurants, parks, shops, etc.) using natural language queries. The system integrates:
- **Local LLM** (via OpenWebUI) - understands user intent and context
- **Google Maps API** - provides accurate location data and place information
- **FastAPI Backend** - securely manages API keys and enforces rate limits
- **Modern Frontend** - responsive UI with embedded maps

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (HTML/CSS/JS)          │
│    - Search interface                   │
│    - Display results with maps          │
│    - Geolocation support                │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│        FastAPI Backend (Python)         │
│    - /search endpoint (Google Maps)     │
│    - /llm-search (LLM integration)      │
│    - Rate limiting & API key security   │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
    ┌────────┐         ┌──────────────┐
    │OpenWebUI           │ Google Maps API
    │LLM        │         │ Places API
    └────────┘         └──────────────┘
```

## 🔧 Installation & Setup

### 🐳 Quick Start with Docker (Recommended)

**One command to run everything:**

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your Google Maps API key to .env
# GOOGLE_MAPS_API_KEY=your_key_here

# 3. Start all services (FastAPI, OpenWebUI, Ollama)
docker-compose up -d

# 4. Open http://localhost:8001 in your browser
```

That's it! See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker instructions.

---

### Manual Setup (Without Docker)

#### Prerequisites
- Python 3.10+
- Google Cloud account with Maps API enabled
- OpenWebUI installed and running locally (optional, for LLM features)

#### 1. Clone/Setup Project
```bash
cd d:\programmings\laragon\www\hey-pico
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy example to .env
copy .env.example .env

# Edit .env and add your Google Maps API key
# GOOGLE_MAPS_API_KEY=your_key_here
```

### 5. Get Google Maps API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable these APIs:
   - Maps SDK for JavaScript
   - Places API
   - Maps Embed API
4. Create an API key (Credentials → Create Credentials → API Key)
5. Restrict key to your domain (optional, recommended for production)

### 6. Start OpenWebUI (Optional)
```bash
docker pull ghcr.io/open-webui/open-webui:latest
docker run -d -p 8000:8080 --name open-webui ghcr.io/open-webui/open-webui:latest
```

### 7. Run the Backend Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

### 8. Access Frontend
Open `http://localhost:8001/` in your browser

## 📚 API Endpoints

### Health Check
```
GET /health
Response: { "status": "healthy", "version": "1.0.0" }
```

### Search Places
```
POST /search
Body: {
    "query": "Italian restaurants",
    "latitude": -33.8688,
    "longitude": 151.2093
}
Response: {
    "query": "Italian restaurants",
    "places": [...],
    "count": 5
}
```

### LLM-Powered Search
```
POST /llm-search
Body: {
    "query": "Where can I get good coffee near me?"
}
Response: { "places": [...], "count": 3 }
```

## 🔐 Security Implementation

### API Key Management
- **Server-side only**: Google Maps API key is stored on backend, never exposed to frontend
- **Environment variables**: Sensitive data loaded from `.env` file (not committed to git)
- **.env in .gitignore**: Production keys never leak to version control

### Rate Limiting
- **Per IP limiting**: Configurable rate limit (default: 30 requests/minute)
- **Middleware**: Applied to all endpoints to prevent abuse
- **Configuration**: Adjust in `.env` → `RATE_LIMIT_PER_MINUTE`
- **Response Headers**: Returns `X-RateLimit-*` headers showing remaining requests
- **HTTP 429**: Returns "Too Many Requests" when limit exceeded with retry-after time

### Data Validation
- **Pydantic models**: Automatic request validation and type checking
- **Input sanitization**: Place queries validated before API calls
- **Error handling**: Graceful error responses without exposing stack traces

## 📝 Key Assumptions

1. **OpenWebUI URL**: Assumed to be running at `http://localhost:8000`
   - Can be changed in `.env` via `OPENWEB_UI_URL`
   - Defaults to mistral model (configurable via `OPENWEB_UI_MODEL`)

2. **Geolocation**: Frontend uses browser's Geolocation API
   - Users must grant permission
   - HTTPS required for production

3. **Google Maps Embed**: Uses free embedding for map display
   - Limited to 25,000 impressions/day in free tier
   - Consider upgrading for higher traffic

4. **LLM Integration**: Currently simplified
   - Real implementation would parse LLM response to extract structured place data
   - Currently uses LLM response directly as search query

5. **CORS Enabled**: Frontend on same machine/localhost
   - For production, restrict to your domain in `main.py`

## 🚀 Deployment Considerations

### Production Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Use environment-specific `.env` files
- [ ] Restrict CORS origins to your domain
- [ ] Enable HTTPS for geolocation
- [ ] Add request logging/monitoring
- [ ] Set up API quota alerts on Google Cloud
- [ ] Use a reverse proxy (nginx) for the frontend
- [ ] Add database for caching frequently searched places
- [ ] Implement proper authentication if needed

### Scaling Options
1. **Caching**: Add Redis for frequently searched places
2. **Async Processing**: Use Celery for long-running LLM queries
3. **Load Balancing**: Deploy multiple backend instances
4. **CDN**: Cache frontend assets globally

## 📦 File Structure
```
hey-pico/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── maps.py              # Google Maps integration
│   ├── llm.py               # OpenWebUI/LLM integration
│   ├── rate_limiter.py      # Rate limiting middleware
│   └── __init__.py
├── frontend/
│   └── index.html           # Web interface
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .env                     # Environment variables (not committed)
├── Dockerfile               # Docker image for backend
├── docker-compose.yml       # Docker orchestration (backend, OpenWebUI, Ollama)
├── .dockerignore            # Docker build exclusions
├── DOCKER_SETUP.md          # Docker setup guide
├── code-test.md             # Original assignment
└── README.md                # This file
```

## 🐛 Troubleshooting

**"API connection refused"**
- Ensure FastAPI server is running: `python -m uvicorn backend.main:app --reload`
- Check port 8001 is not blocked

**"Google Maps API Key invalid"**
- Verify key in `.env` is correct
- Check API quotas in Google Cloud Console
- Ensure `Places API` is enabled

**"LLM not responding"**
- Verify OpenWebUI is running: `docker ps`
- Check `OPENWEB_UI_URL` in `.env`
- Try accessing `http://localhost:8000` directly

**"Rate limit exceeded"**
- Wait before making more requests, or increase `RATE_LIMIT_PER_MINUTE` in `.env`

## 📄 License

This project is for educational purposes as per the code challenge requirements.

---

**Author's Notes:**
- This implementation prioritizes security and clean architecture
- Rate limiting and key management are production-ready patterns
- The LLM integration is scaffolded and ready for enhancement
- Consider adding response caching to reduce API costs
