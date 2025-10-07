# Telegram Image Colorization Bot

A modern Python Telegram bot built with **aiogram 3.x** that uses AI to colorize black and white images using a Caffe model, with comprehensive PostgreSQL statistics tracking and Redis caching.

## 🚀 Features

- 🤖 **AI-powered image colorization** using Caffe models
- 📱 **Modern aiogram 3.x framework** with async/await support
- 🎨 **High-quality colorization results** with post-processing
- 📸 **Support for various image formats** (JPG, PNG, etc.)
- ⚡ **Fast processing** with Redis caching
- 📊 **Comprehensive statistics tracking** with PostgreSQL
- 👥 **User management** and activity monitoring
- 🔒 **Rate limiting** to prevent abuse
- 👨‍💼 **Admin commands** for statistics and monitoring
- 🗄️ **Database migrations** with Alembic
- 🚀 **Production-ready** with proper error handling

## 🛠 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

#### PostgreSQL Setup:

```bash
# Install PostgreSQL
# Create database
createdb colorization_bot

# Set database URL
export DATABASE_URL="postgresql://username:password@localhost:5432/colorization_bot"
```

#### Redis Setup:

```bash
# Install Redis
# Start Redis server
redis-server

# Set Redis URL
export REDIS_URL="redis://localhost:6379/0"
```

### 3. Environment Configuration

Copy `env_example.txt` to `.env` and configure:

```bash
cp env_example.txt .env
```

Edit `.env` file:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
DATABASE_URL=postgresql://username:password@localhost:5432/colorization_bot
REDIS_URL=redis://localhost:6379/0
MODEL_PATH=models/colorization_release_v2.caffemodel
PROTOTXT_PATH=models/colorization_deploy_v2.prototxt
```

### 4. Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init migrations

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Get a Telegram Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token to your `.env` file

### 6. Add Your Caffe Model Files

Place your Caffe model files in the `models/` directory:

- `colorization_release_v2.caffemodel` (model weights)
- `colorization_deploy_v2.prototxt` (model architecture)

### 7. Run the Bot

```bash
python bot.py
```

## 📱 Usage

### User Commands:

- `/start` - Welcome message and bot introduction
- `/help` - Detailed help and usage instructions
- `/about` - Information about the bot
- `/stats` - Your personal statistics
- `/language` - Change bot language

### Admin Commands:

- `/admin_stats` - Global statistics and analytics (admin only)

### Supported Languages:

- 🇺🇸 **English** (en)
- 🇷🇺 **Russian** (ru)
- 🇺🇿 **Uzbek** (uz)
- 🇺🇦 **Ukrainian** (uk)

### Image Processing:

1. Send a black and white image to the bot
2. Wait for processing (usually 5-15 seconds)
3. Receive your colorized image!

## 📊 Statistics & Analytics

The bot tracks comprehensive statistics:

### User Statistics:

- Total requests made
- Images processed successfully
- Processing times
- Activity history
- User profile information
- Language preferences

### Global Statistics:

- Total users and active users
- Request success rates
- Average processing times
- Top users by activity
- Request types breakdown

### Admin Dashboard:

- Real-time statistics
- User activity monitoring
- Performance metrics
- Error tracking

## 🏗 Architecture

### Tech Stack:

- **Framework**: aiogram 3.x (async Telegram Bot API)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for rate limiting and performance
- **AI Model**: Caffe for image colorization
- **Image Processing**: OpenCV, Pillow
- **Migrations**: Alembic for database schema management

### Key Components:

- `bot.py` - Main bot application with aiogram handlers
- `database.py` - Database models and operations
- `model_loader.py` - Caffe model integration
- `utils.py` - Image processing utilities
- `config.py` - Configuration management
- `languages.py` - Multi-language support system

## 📁 Project Structure

```
tg bot/
├── bot.py                    # Main bot application
├── database.py              # Database models and operations
├── model_loader.py          # Caffe model integration
├── utils.py                 # Image processing utilities
├── config.py                # Configuration management
├── languages.py             # Multi-language support system
├── requirements.txt         # Python dependencies
├── env_example.txt          # Environment variables template
├── alembic.ini              # Alembic configuration
├── migrations/               # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_add_language_support.py
├── models/                  # Caffe model files
│   ├── colorization_release_v2.caffemodel
│   ├── colorization_deploy_v2.prototxt
│   └── README.md
└── README.md                # This file
```

## ⚙️ Configuration Options

### Bot Settings:

- `BOT_TOKEN` - Telegram bot token
- `ADMIN_IDS` - Comma-separated list of admin user IDs
- `RATE_LIMIT_PER_USER` - Max requests per user per hour
- `MAX_FILE_SIZE` - Maximum image file size
- `PROCESSING_TIMEOUT` - Timeout for image processing

### Database Settings:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `ENABLE_STATISTICS` - Enable/disable statistics tracking

### Model Settings:

- `MODEL_PATH` - Path to Caffe model file
- `PROTOTXT_PATH` - Path to Caffe prototxt file
- `MODEL_INPUT_SIZE` - Model input image size

## 🔧 Advanced Features

### Rate Limiting:

- Per-user rate limiting with Redis
- Configurable request limits
- Automatic cleanup of expired limits

### Caching:

- Redis-based caching for improved performance
- Configurable cache TTL
- Automatic cache invalidation

### Error Handling:

- Comprehensive error logging
- User-friendly error messages
- Automatic retry mechanisms

### Database Optimization:

- Connection pooling
- Async database operations
- Automatic cleanup of old data

## 🚀 Production Deployment

### Environment Variables:

```bash
export BOT_TOKEN="your_production_bot_token"
export DATABASE_URL="postgresql://user:pass@prod-db:5432/colorization_bot"
export REDIS_URL="redis://prod-redis:6379/0"
export ADMIN_IDS="123456789,987654321"
```

### Database Setup:

```bash
# Run migrations
alembic upgrade head

# Optional: Seed initial data
python -c "from database import DatabaseManager; import asyncio; asyncio.run(DatabaseManager('your_db_url').init_database())"
```

### Monitoring:

- Check logs for errors and performance
- Monitor database and Redis connections
- Track user statistics and usage patterns

## 🐛 Troubleshooting

### Common Issues:

1. **Database Connection Issues**:

   - Check PostgreSQL is running
   - Verify DATABASE_URL format
   - Ensure database exists

2. **Redis Connection Issues**:

   - Check Redis server is running
   - Verify REDIS_URL format
   - Test Redis connectivity

3. **Model Loading Issues**:

   - Verify model files exist
   - Check file permissions
   - Ensure Caffe is properly installed

4. **Rate Limiting Issues**:
   - Check Redis connection
   - Verify rate limit settings
   - Clear Redis cache if needed

### Error Messages:

- "Database connection failed": Check DATABASE_URL and PostgreSQL
- "Redis connection failed": Check REDIS_URL and Redis server
- "Model file not found": Verify model files in models/ directory
- "Rate limit exceeded": User has exceeded hourly request limit

## 📈 Performance Optimization

### Database:

- Use connection pooling
- Index frequently queried columns
- Regular cleanup of old data
- Monitor query performance

### Redis:

- Configure appropriate memory limits
- Use Redis persistence if needed
- Monitor cache hit rates
- Set appropriate TTL values

### Model:

- Preload model on startup
- Use GPU acceleration if available
- Optimize image preprocessing
- Cache model predictions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For support and questions:

- Check the troubleshooting section
- Review the logs for error details
- Ensure all dependencies are properly installed
- Verify configuration settings
