# Automation Server

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/odense-rpa/automation-server)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/odense-rpa/automation-server/issues)

**A complete environment for running and managing Python-based automations with a REST API, web interface, and isolated worker environment.**

## ✨ Features

- 🚀 **REST API** - Complete FastAPI backend for automation management
- 🎯 **Web Interface** - Vue.js frontend for easy task management  
- 🔒 **Isolated Workers** - Secure Python script execution environment
- 📊 **Scheduling** - Cron-based and event-driven task scheduling
- 🐳 **Docker Ready** - Production-ready containerized deployment
- 🎭 **Playwright Support** - Web automation capabilities built-in

## 🚀 Quick Start

1. **Clone and setup environment**:
   ```bash
   git clone https://github.com/odense-rpa/automation-server.git
   cd automation-server
   cp .env.example .env
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - **Web Interface**: http://localhost
   - **API Documentation**: http://localhost/api/docs
   - **Database Admin** (optional): http://localhost:8080

The system is now running with PostgreSQL database, REST API, web interface, and 2 worker nodes.

## 🏗️ What You Get

The Automation Server consists of three main components:

### 🖥️ Backend API
- Authentication and authorization
- Task scheduling and management
- Resource management
- Health monitoring and logging

### 🌐 Frontend Interface  
- Task creation and monitoring
- Real-time execution status
- Workqueue monitoring
- Worker management dashboard

### ⚙️ Worker Environment
- Isolated Python script execution
- Support for web automation (Playwright)
- Scalable worker deployment

## 📦 Installation Options

### Development Setup

Use this setup for local development and testing:

```bash
# Start with database admin tools
docker-compose --profile tools up -d

# Or standard setup
docker-compose up -d
```

### Production Setup

For production deployments:

```bash
# Copy and customize production config
cp docker-compose.prod-example.yml docker-compose.prod.yml
cp .env.example .env

# Edit .env with your production values
# Then start
docker-compose -f docker-compose.prod.yml up -d
```

You should also consider adding SSL certificates to your production environment. Also setup tokens in the administration interface 

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
POSTGRES_USER=ats_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=ats

# Workers  
ATS_TOKEN=your-api-token-here   # Can be left blank for development
ATS_CAPABILITIES=playwright     # If using the built-in worker with playwright 

# Timezone
TZ=Europe/Copenhagen
```

### Adding More Workers

Scale workers by adding to `docker-compose.yml`:

```yaml
worker03:
  <<: *worker-template
  hostname: worker-03
```

## 📝 Usage Examples

TODO: Write a process development guide.


## 📚 API Documentation

- **Interactive Documentation**: http://localhost/api/docs
- **OpenAPI Spec**: http://localhost/api/openapi.json

## 🛠️ Development

### Local Development

```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend  
cd frontend
npm install
npm run dev

# Worker
cd worker
uv sync
uv run main.py
```

### Running Tests

```bash
# Backend tests
cd backend && uv run pytest

# Frontend tests
cd frontend && npm test
```

Be aware that the backend tests require docker to be available as it will spin up a local postgresql container for e2e testing.

## 🚀 Deployment

### Building Images

```bash
# Build all images
docker-compose build

# Or build individual components
cd worker && ./build-standard.sh      # Standard worker
cd worker && ./build-playwright.sh    # Playwright-enabled worker
```

### Production Considerations

- Use specific image tags instead of `latest`
- Set up SSL certificates for HTTPS
- Configure proper database backups
- Monitor with health checks
- Use Docker secrets for sensitive data

## 🔧 Troubleshooting  

**Worker not processing tasks**:
```bash
# Check worker logs
docker-compose logs worker01

# Verify API connectivity
docker-compose exec worker01 curl http://api:8000/health
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Check our [issues](https://github.com/odense-rpa/automation-server/issues) for planned features
2. Open an issue to discuss your idea
3. Fork the repository and create a feature branch
4. Make your changes and add tests
5. Submit a pull request

For detailed documentation, see the [docs/](docs/) directory.