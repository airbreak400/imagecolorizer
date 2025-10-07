import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE').strip().strip('"').strip("'")
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/colorization_bot')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Model Configuration
MODEL_PATH = os.getenv('MODEL_PATH', 'models/colorization_release_v2.caffemodel')
PROTOTXT_PATH = os.getenv('PROTOTXT_PATH', 'models/colorization_deploy_v2.prototxt')

# Image Processing Settings
MAX_IMAGE_SIZE = 1024  # Maximum image dimension in pixels
MODEL_INPUT_SIZE = 224  # Model input size (224x224 for most colorization models)

# Bot Settings
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB max file size
PROCESSING_TIMEOUT = 60  # 60 seconds timeout for processing
RATE_LIMIT_PER_USER = 50  # Max requests per user per hour (increased from 10)
CACHE_TTL = 3600  # Cache TTL in seconds

# High Load Optimizations
MAX_CONCURRENT_REQUESTS = 50  # Уменьшено с 100
DB_POOL_MIN_SIZE = 5          # Уменьшено с 50
DB_POOL_MAX_SIZE = 20         # Уменьшено с 200
REDIS_POOL_SIZE = 50          # Уменьшено с 100        # Redis connection pool size
IMAGE_CACHE_TTL = 86400       # 24 hours cache for processed images
MEMORY_LIMIT_MB = 2048        # 2GB memory limit
CLEANUP_INTERVAL = 300        # 5 minutes cleanup interval
HEALTH_CHECK_INTERVAL = 60    # 1 minute health checks
THREAD_POOL_SIZE = 20         # Thread pool size for image processing

# Performance Monitoring
ENABLE_PERFORMANCE_MONITORING = True
METRICS_RETENTION_HOURS = 24
AUTO_CLEANUP_ENABLED = True

# Statistics Settings
ENABLE_STATISTICS = True
STATISTICS_RETENTION_DAYS = 365