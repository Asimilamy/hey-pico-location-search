# Docker Quick Start Setup

This file helps first-time users set up the docker environment.

## 📋 Prerequisites

- Docker Desktop installed (https://www.docker.com/products/docker-desktop)
- Docker Compose (comes with Docker Desktop)
- Google Maps API Key
- OpenWebUI API Key (generated after first login)

## 🚀 Quick Setup (5 minutes)

### Step 1: Create `.env` file

Copy `.env.example` to `.env` and add your Google Maps API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
GOOGLE_MAPS_API_KEY=your_apis_key_here
OPENWEB_UI_API_KEY=will_be_generated_after_login
```

**Note:** You can leave `OPENWEB_UI_API_KEY` empty for now, we'll generate it.

### Step 2: Start Docker Containers

```bash
docker-compose up -d
```

This will:
- ✅ Build the FastAPI backend
- ✅ Start OpenWebUI (http://localhost:8000)
- ✅ Start Ollama for local LLM (http://localhost:11434)
- ✅ Start FastAPI backend (http://localhost:8001)

Wait 30-60 seconds for all services to start.

### Step 3: Set Up OpenWebUI

1. Go to **http://localhost:8000**
2. Create an account/login
3. Download a model:
   - Go to **Settings** → **Connections** → **Ollama**
   - Verify it connects to `http://ollama:11434`
   - Go back to main chat, click the model selector
   - Search for and pull **mistral** (or llama2, neural-chat)
   - Wait for download (~5-10 minutes)

### Step 4: Get OpenWebUI API Key

1. In OpenWebUI, click your **profile icon** (bottom left)
2. Go to **Settings** → Find **API Keys** section
3. Generate a new API key
4. Copy it and paste into your `.env` file: `OPENWEB_UI_API_KEY=sk_...`

### Step 5: Restart Backend

```bash
docker-compose restart backend
```

### Step 6: Test the Application

Go to **http://localhost:8001** and search for places!

Example: *"I want coffee"* → LLM interprets → Google Maps finds coffee shops

---

## 📊 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **LLM Maps App** | http://localhost:8001 | Main application frontend |
| **OpenWebUI** | http://localhost:8000 | LLM chat interface & settings |
| **Ollama** | http://localhost:11434 | Local LLM engine (API only) |

---

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (cleans up data)
docker-compose down -v
```

---

## 🔄 Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart open-webui
```

---

## 📖 Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f open-webui
docker-compose logs -f ollama
```

---

## 🐛 Troubleshooting

### OpenWebUI shows "No models"
- Make sure Ollama is running: `docker-compose logs ollama`
- Download a model in OpenWebUI settings
- Wait for download to complete

### "Model not found" error
- Verify model name matches what you pulled in OpenWebUI
- Default is `mistral` - if you pulled something else, update `.env` OPENWEB_UI_MODEL

### Backend can't connect to OpenWebUI
- Check OpenWebUI is running: `docker-compose logs open-webui`
- Verify API key in `.env` is correct
- Connection URL should be `http://open-webui:8080` (not localhost)

### Port already in use
Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "9001:8001"  # Change first 9001 to an available port
```

---

## 📦 Updating the Application

```bash
# Rebuild after code changes
docker-compose up -d --build

# Or rebuild specific service
docker-compose up -d --build backend
```

---

## 🚀 Production Deployment

For production, consider:
1. Using a `.env.prod` file with secure credentials
2. Setting `DEBUG=False` in environment
3. Using environment variables instead of `.env` file
4. Adding reverse proxy (nginx) for SSL/HTTPS
5. Using external Redis for rate limiting at scale
6. Mounting volumes for data persistence

See README.md for more details.

---

**Questions?** Check the main README.md or the code comments for more info!
