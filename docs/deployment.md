# Deployment

TODO: Finish this page up and clean it up.

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
