# Local Development

This document is a work in progress. To be updated

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
