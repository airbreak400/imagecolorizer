# Docker Setup for Telegram Colorization Bot

This guide will help you set up and run the Telegram Colorization Bot using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Git

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd tg-bot

# Copy the environment template
cp env.docker .env
```

### 2. Configure Environment

Edit the `.env` file with your actual values:

```bash
# Required: Get your bot token from @BotFather on Telegram
BOT_TOKEN=your_actual_bot_token_here

# Required: Add your Telegram user ID (get it from @userinfobot)
ADMIN_IDS=123456789,987654321

# Optional: Adjust other settings as needed
```

### 3. Download Model Files

The bot requires Caffe model files. You need to download them:

```bash
# Create models directory
mkdir -p models

# Download the model files (you'll need to get these from the original source)
# Place colorization_release_v2.caffemodel and colorization_deploy_v2.prototxt in the models/ directory
# Also download pts_in_hull.npy and place it in models/
```

### 4. Run the Bot

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down
```

## Services Included

### Core Services
- **bot**: The main Telegram bot application
- **postgres**: PostgreSQL database for storing user data and statistics
- **redis**: Redis cache for performance optimization

### Optional Admin Services
- **pgadmin**: Web interface for PostgreSQL database management (port 8080)
- **redis-commander**: Web interface for Redis management (port 8081)

To start with admin interfaces:
```bash
docker-compose --profile admin up -d
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token (required) | - |
| `ADMIN_IDS` | Comma-separated list of admin user IDs | - |
| `MAX_CONCURRENT_REQUESTS` | Maximum concurrent image processing | 50 |
| `DB_POOL_MIN_SIZE` | Minimum database connections | 10 |
| `DB_POOL_MAX_SIZE` | Maximum database connections | 50 |
| `RATE_LIMIT_PER_USER` | Requests per user per hour | 30 |

### Model Files

The bot requires these model files in the `models/` directory:
- `colorization_release_v2.caffemodel` - The main Caffe model
- `colorization_deploy_v2.prototxt` - Model architecture file
- `pts_in_hull.npy` - Colorization points file

## Monitoring and Management

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f bot
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Database Management
```bash
# Access PostgreSQL directly
docker-compose exec postgres psql -U bot_user -d colorization_bot

# Run database migrations
docker-compose exec bot python -m alembic upgrade head
```

### Health Checks
```bash
# Check service status
docker-compose ps

# Check health
docker-compose exec bot python -c "import sys; print('Bot is healthy')"
```

## Performance Optimization

### Resource Limits

The Docker setup is optimized for moderate usage. For high-traffic scenarios:

1. **Increase database connections**:
   ```env
   DB_POOL_MIN_SIZE=20
   DB_POOL_MAX_SIZE=100
   ```

2. **Adjust Redis memory**:
   ```yaml
   # In docker-compose.yml, redis service
   command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
   ```

3. **Scale the bot service**:
   ```bash
   docker-compose up -d --scale bot=3
   ```

### Monitoring

Access admin interfaces:
- **pgAdmin**: http://localhost:8080 (admin@bot.local / admin123)
- **Redis Commander**: http://localhost:8081

## Troubleshooting

### Common Issues

1. **Bot not starting**:
   ```bash
   # Check logs
   docker-compose logs bot
   
   # Verify environment variables
   docker-compose exec bot env | grep BOT_TOKEN
   ```

2. **Database connection issues**:
   ```bash
   # Check database health
   docker-compose exec postgres pg_isready -U bot_user
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

3. **Model files missing**:
   ```bash
   # Check if model files exist
   docker-compose exec bot ls -la models/
   ```

### Performance Issues

1. **High memory usage**:
   - Reduce `MAX_CONCURRENT_REQUESTS`
   - Lower `DB_POOL_MAX_SIZE`
   - Enable Redis memory limits

2. **Slow processing**:
   - Increase `THREAD_POOL_SIZE`
   - Check Redis cache hit rate
   - Monitor database performance

## Backup and Maintenance

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U bot_user colorization_bot > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U bot_user colorization_bot < backup.sql
```

### Cleanup Old Data
```bash
# The bot automatically cleans up old data, but you can manually trigger:
docker-compose exec bot python -c "
from database import DatabaseManager
import asyncio
async def cleanup():
    db = DatabaseManager('postgresql://bot_user:bot_password@postgres:5432/colorization_bot')
    await db.init_database()
    await db.cleanup_old_data(30)  # Keep last 30 days
    await db.close()
asyncio.run(cleanup())
"
```

## Production Deployment

For production deployment:

1. **Use environment-specific configs**
2. **Set up proper secrets management**
3. **Configure reverse proxy (nginx)**
4. **Set up monitoring and alerting**
5. **Configure automated backups**
6. **Use Docker Swarm or Kubernetes for scaling**

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify all environment variables are set
3. Ensure model files are present
4. Check database and Redis connectivity

