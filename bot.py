import asyncio
import logging
import cv2
import numpy as np
import tempfile
import os
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import redis.asyncio as redis

from model_loader import CaffeColorizationModel
from utils import validate_image, resize_image_if_needed, enhance_colorized_image
from database import DatabaseManager
from languages import Language, get_translation, get_language_from_code, get_supported_languages, LANGUAGE_NAMES
from performance import (
    PerformanceMonitor, ImageCache, AsyncImageProcessor, ResourceManager,
    LoadBalancer, HealthChecker, MetricsCollector, OptimizedConnectionPool
)
from config import (
    BOT_TOKEN, MODEL_PATH, PROTOTXT_PATH, DATABASE_URL, REDIS_URL,
    ADMIN_IDS, RATE_LIMIT_PER_USER, CACHE_TTL, ENABLE_STATISTICS,
    MAX_CONCURRENT_REQUESTS, DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE,
    IMAGE_CACHE_TTL, THREAD_POOL_SIZE, HEALTH_CHECK_INTERVAL,
    ENABLE_PERFORMANCE_MONITORING, AUTO_CLEANUP_ENABLED
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States
class UserStates(StatesGroup):
    waiting_for_image = State()

class ColorizationBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        self.model = None
        self.db = None
        self.redis = None
        
        # Performance optimization components
        self.performance_monitor = PerformanceMonitor()
        self.image_cache = None
        self.async_processor = None
        self.resource_manager = None
        self.load_balancer = None
        self.health_checker = None
        self.metrics_collector = None
        self.connection_pool = None
        
        self.setup_handlers()
    
    async def init_services(self):
        """Initialize all services with performance optimizations"""
        try:
            # Initialize connection pools first
            self.connection_pool = OptimizedConnectionPool(DATABASE_URL, REDIS_URL)
            await self.connection_pool.init_pools(DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE)
            
            # Load model
            self.model = CaffeColorizationModel(MODEL_PATH, PROTOTXT_PATH)
            logger.info("Caffe model loaded successfully")
            
            # Initialize database with optimized pool
            self.db = DatabaseManager(DATABASE_URL)
            await self.db.init_database(DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE)
            logger.info("Database initialized successfully")
            
            # Initialize Redis with connection pool
            self.redis = redis.Redis(connection_pool=self.connection_pool.redis_pool)
            await self.redis.ping()
            logger.info("Redis connected successfully")
            
            # Initialize performance optimization components
            self.image_cache = ImageCache(self.redis, IMAGE_CACHE_TTL)
            self.async_processor = AsyncImageProcessor(THREAD_POOL_SIZE)
            self.resource_manager = ResourceManager()
            self.load_balancer = LoadBalancer(MAX_CONCURRENT_REQUESTS)
            self.metrics_collector = MetricsCollector(self.redis)
            self.health_checker = HealthChecker(self.db, self.redis, self.model)
            
            # Start background tasks
            if AUTO_CLEANUP_ENABLED:
                asyncio.create_task(self.resource_manager.periodic_cleanup())
            
            if ENABLE_PERFORMANCE_MONITORING:
                asyncio.create_task(self.health_checker.start_health_monitoring(HEALTH_CHECK_INTERVAL))
            
            logger.info("All services initialized with performance optimizations")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise
    
    async def close_services(self):
        """Close all services"""
        try:
            if self.async_processor:
                self.async_processor.shutdown()
            
            if self.connection_pool:
                await self.connection_pool.close_pools()
            
            if self.db:
                await self.db.close()
            
            if self.redis:
                await self.redis.close()
            
            await self.bot.session.close()
            
            logger.info("All services closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing services: {e}")
    
    def setup_handlers(self):
        """Setup bot handlers"""
        # Command handlers
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.about_command, Command("about"))
        self.dp.message.register(self.stats_command, Command("stats"))
        self.dp.message.register(self.admin_stats_command, Command("admin_stats"))
        self.dp.message.register(self.performance_command, Command("performance"))
        self.dp.message.register(self.health_command, Command("health"))
        self.dp.message.register(self.language_command, Command("language"))
        
        # Callback handlers
        self.dp.callback_query.register(self.handle_language_callback, F.data.startswith("lang_"))
        
        # Message handlers
        self.dp.message.register(self.handle_image, F.photo)
        self.dp.message.register(self.handle_text, F.text)
        
        # Error handler
        self.dp.error.register(self.error_handler)
    
    async def check_rate_limit(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit"""
        if not self.redis:
            return True
        
        key = f"rate_limit:{user_id}"
        current_requests = await self.redis.get(key)
        
        if current_requests is None:
            await self.redis.setex(key, 3600, 1)  # 1 hour TTL
            return True
        
        if int(current_requests) >= RATE_LIMIT_PER_USER:
            return False
        
        await self.redis.incr(key)
        return True
    
    async def get_or_create_user(self, message: Message) -> Dict[str, Any]:
        """Get or create user in database"""
        user = message.from_user
        return await self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code or 'en',
            is_premium=getattr(user, 'is_premium', False)
        )
    
    async def get_user_language(self, user_id: int) -> Language:
        """Get user's language preference"""
        if not self.db:
            return Language.ENGLISH
        
        language_code = await self.db.get_user_language(user_id)
        return get_language_from_code(language_code)
    
    def create_language_keyboard(self) -> InlineKeyboardMarkup:
        """Create language selection keyboard"""
        builder = InlineKeyboardBuilder()
        
        for language in get_supported_languages():
            builder.button(
                text=LANGUAGE_NAMES[language],
                callback_data=f"lang_{language.value}"
            )
        
        builder.adjust(2)  # 2 buttons per row
        return builder.as_markup()
    
    async def log_request(self, user_id: int, request_type: str, **kwargs):
        """Log user request"""
        if ENABLE_STATISTICS and self.db:
            await self.db.log_request(user_id, request_type, **kwargs)
    
    async def start_command(self, message: Message):
        """Handle /start command"""
        user = await self.get_or_create_user(message)
        user_language = await self.get_user_language(user.telegram_id)
        
        # Check if user is new (first time using bot)
        if user.total_requests == 0:
            # Show language selection for new users
            keyboard = self.create_language_keyboard()
            await message.reply(
                get_translation(user_language, "language_selection"),
                reply_markup=keyboard
            )
        else:
            # Show welcome message in user's language
            welcome_text = get_translation(user_language, "welcome")
            await message.reply(welcome_text)
        
        await self.log_request(user.telegram_id, 'start')
    
    async def help_command(self, message: Message):
        """Handle /help command"""
        user_language = await self.get_user_language(message.from_user.id)
        help_text = get_translation(user_language, "help")
        
        await message.reply(help_text)
        await self.log_request(message.from_user.id, 'help')
    
    async def about_command(self, message: Message):
        """Handle /about command"""
        user_language = await self.get_user_language(message.from_user.id)
        about_text = get_translation(user_language, "about")
        
        await message.reply(about_text)
        await self.log_request(message.from_user.id, 'about')
    
    async def stats_command(self, message: Message):
        """Handle /stats command"""
        user_id = message.from_user.id
        user_language = await self.get_user_language(user_id)
        
        if not self.db:
            await message.reply(get_translation(user_language, "stats_unavailable"))
            return
        
        try:
            stats = await self.db.get_user_stats(user_id)
            user_data = stats.get('user', {})
            
            stats_text = get_translation(
                user_language, "stats",
                username=user_data.get('username', 'N/A'),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                created_at=user_data.get('created_at', 'N/A'),
                total_requests=user_data.get('total_requests', 0),
                total_images_processed=user_data.get('total_images_processed', 0),
                last_activity=user_data.get('last_activity', 'N/A')
            )
            
            await message.reply(stats_text)
            await self.log_request(user_id, 'stats')
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            await message.reply(get_translation(user_language, "stats_error"))
    
    async def admin_stats_command(self, message: Message):
        """Handle /admin_stats command"""
        user_id = message.from_user.id
        user_language = await self.get_user_language(user_id)
        
        if user_id not in ADMIN_IDS:
            await message.reply(get_translation(user_language, "admin_denied"))
            return
        
        if not self.db:
            await message.reply(get_translation(user_language, "stats_unavailable"))
            return
        
        try:
            global_stats = await self.db.get_global_stats(30)
            top_users = await self.db.get_top_users(5)
            
            # Format top users
            top_users_text = ""
            for i, user in enumerate(top_users, 1):
                top_users_text += f"{i}. @{user.get('username', 'N/A')} - {user.get('total_requests', 0)} requests\n"
            
            admin_text = get_translation(
                user_language, "admin_stats",
                total_users=global_stats.get('total_users', 0),
                active_users=global_stats.get('active_users', 0),
                total_requests=global_stats.get('total_requests', 0),
                successful_requests=global_stats.get('successful_requests', 0),
                failed_requests=global_stats.get('failed_requests', 0),
                success_rate=global_stats.get('success_rate', 0),
                average_processing_time=global_stats.get('average_processing_time', 0),
                top_users=top_users_text
            )
            
            await message.reply(admin_text)
            await self.log_request(user_id, 'admin_stats')
            
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
            await message.reply(get_translation(user_language, "admin_stats_error"))
    
    async def performance_command(self, message: Message):
        """Handle /performance command - show performance metrics"""
        user_id = message.from_user.id
        user_language = await self.get_user_language(user_id)
        
        if user_id not in ADMIN_IDS:
            await message.reply(get_translation(user_language, "admin_denied"))
            return
        
        try:
            # Get system stats
            system_stats = self.performance_monitor.get_system_stats()
            
            # Get cache stats
            cache_stats = self.image_cache.get_cache_stats() if self.image_cache else {}
            
            # Get load balancer stats
            load_stats = self.load_balancer.get_stats() if self.load_balancer else {}
            
            # Get processor stats
            processor_stats = self.async_processor.get_stats() if self.async_processor else {}
            
            performance_text = f"""
📊 Performance Metrics

🖥️ System:
• CPU: {system_stats.get('cpu_percent', 0):.1f}%
• Memory: {system_stats.get('memory_percent', 0):.1f}%
• Disk: {system_stats.get('disk_percent', 0):.1f}%

📈 Requests:
• Active: {system_stats.get('active_requests', 0)}
• Total: {system_stats.get('total_requests', 0)}
• Max Concurrent: {system_stats.get('max_concurrent', 0)}
• Avg Processing: {system_stats.get('avg_processing_time', 0):.2f}s
• Error Rate: {system_stats.get('error_rate', 0):.1f}%

💾 Cache:
• Hits: {cache_stats.get('cache_hits', 0)}
• Misses: {cache_stats.get('cache_misses', 0)}
• Hit Rate: {cache_stats.get('hit_rate', 0):.1f}%

⚖️ Load Balancer:
• Active: {load_stats.get('active_requests', 0)}
• Max: {load_stats.get('max_concurrent', 0)}
• Queue: {load_stats.get('queue_size', 0)}

🔧 Processor:
• Active Tasks: {processor_stats.get('active_tasks', 0)}
• Max Tasks: {processor_stats.get('max_active_tasks', 0)}
• Workers: {processor_stats.get('max_workers', 0)}
            """
            
            await message.reply(performance_text)
            await self.log_request(user_id, 'performance')
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            await message.reply("❌ Error retrieving performance metrics.")
    
    async def health_command(self, message: Message):
        """Handle /health command - show system health"""
        user_id = message.from_user.id
        user_language = await self.get_user_language(user_id)
        
        if user_id not in ADMIN_IDS:
            await message.reply(get_translation(user_language, "admin_denied"))
            return
        
        try:
            health = await self.health_checker.check_health()
            
            status_emoji = {
                'healthy': '✅',
                'degraded': '⚠️',
                'critical': '❌'
            }
            
            health_text = f"""
🏥 System Health

Overall Status: {status_emoji.get(health.get('overall_status', 'unknown'), '❓')} {health.get('overall_status', 'unknown').upper()}

Components:
• Database: {health.get('components', {}).get('database', 'unknown')}
• Redis: {health.get('components', {}).get('redis', 'unknown')}
• Model: {health.get('components', {}).get('model', 'unknown')}

System Resources:
{health.get('components', {}).get('system', {})}

Last Check: {health.get('timestamp', 'unknown')}
            """
            
            await message.reply(health_text)
            await self.log_request(user_id, 'health')
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            await message.reply("❌ Error retrieving health status.")
    
    async def language_command(self, message: Message):
        """Handle /language command"""
        user_language = await self.get_user_language(message.from_user.id)
        keyboard = self.create_language_keyboard()
        
        await message.reply(
            get_translation(user_language, "language_selection"),
            reply_markup=keyboard
        )
        await self.log_request(message.from_user.id, 'language')
    
    async def handle_language_callback(self, callback: CallbackQuery):
        """Handle language selection callback"""
        user_id = callback.from_user.id
        language_code = callback.data.split("_")[1]
        language = get_language_from_code(language_code)
        
        # Update user's language preference
        if self.db:
            await self.db.update_user_language(user_id, language_code)
        
        # Send confirmation message
        await callback.message.edit_text(
            get_translation(language, "language_changed", language=LANGUAGE_NAMES[language])
        )
        
        # Send welcome message in new language
        welcome_text = get_translation(language, "welcome")
        await callback.message.answer(welcome_text)
        
        await self.log_request(user_id, 'language_change', extra_data={'new_language': language_code})
    
    async def handle_image(self, message: Message):
        """Handle incoming images with performance optimizations"""
        user_id = message.from_user.id
        user_language = await self.get_user_language(user_id)
        
        # Performance monitoring
        self.performance_monitor.increment_request()
        
        try:
            # Check rate limit
            if not await self.check_rate_limit(user_id):
                await message.reply(
                    get_translation(user_language, "rate_limit", limit=RATE_LIMIT_PER_USER)
                )
                return
            
            # Get user
            user = await self.get_or_create_user(message)
            
            # Get the highest resolution photo
            photo = message.photo[-1]
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_input:
                temp_input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            # Register temp files for cleanup
            self.resource_manager.register_temp_file(temp_input_path)
            self.resource_manager.register_temp_file(temp_output_path)
            
            try:
                # Download image
                await self.bot.download(photo, temp_input_path)
                
                # Validate image
                is_valid, error_message = validate_image(temp_input_path)
                if not is_valid:
                    await message.reply(get_translation(user_language, "invalid_image", error_message=error_message))
                    await self.log_request(user_id, 'colorize', success=False, error_message=error_message)
                    self.performance_monitor.record_error()
                    return
                
                # Resize if needed
                resize_image_if_needed(temp_input_path)
                
                # Check cache first
                cached_result = await self.image_cache.get_cached_result(temp_input_path)
                if cached_result:
                    # Send cached result using BufferedInputFile
                    photo_file = BufferedInputFile(cached_result, filename="colorized.jpg")
                    await message.answer_photo(
                        photo=photo_file,
                        caption=get_translation(user_language, "colorized_result")
                    )
                    
                    # Log cached request
                    await self.log_request(
                        user_id, 'colorize',
                        file_id=photo.file_id,
                        file_size=photo.file_size,
                        processing_time=0.1,  # Very fast for cached results
                        success=True
                    )
                    
                    self.performance_monitor.decrement_request()
                    return
                
                # Send processing message
                processing_msg = await message.reply(get_translation(user_language, "processing"))
                
                # Process image with load balancing and async processing
                start_time = time.time()
                
                # Use load balancer to manage concurrent requests
                colorized_image = await self.load_balancer.process_request(
                    self.async_processor.process_image_async,
                    self.model.colorize,
                    temp_input_path
                )
                
                processing_time = time.time() - start_time
                self.performance_monitor.record_processing_time(processing_time)
                
                # Enhance the colorized image
                enhanced_image = enhance_colorized_image(colorized_image)
                
                # Save colorized image
                cv2.imwrite(temp_output_path, enhanced_image)
                
                # Cache the result for future use
                with open(temp_output_path, 'rb') as f:
                    result_bytes = f.read()
                    await self.image_cache.cache_result(temp_input_path, result_bytes)
                
                # Send the colorized image using FSInputFile
                await message.answer_photo(
                    photo=FSInputFile(temp_output_path),
                    caption=get_translation(user_language, "colorized_result")
                )
                
                # Delete processing message
                await processing_msg.delete()
                
                # Log successful request
                await self.log_request(
                    user_id, 'colorize',
                    file_id=photo.file_id,
                    file_size=photo.file_size,
                    processing_time=processing_time,
                    success=True
                )
                
                # Record metrics
                if self.metrics_collector:
                    await self.metrics_collector.record_metric('processing_time', processing_time)
                    await self.metrics_collector.record_metric('request_count', 1)
                
            finally:
                # Clean up temporary files
                self.resource_manager.unregister_temp_file(temp_input_path)
                self.resource_manager.unregister_temp_file(temp_output_path)
                
                if os.path.exists(temp_input_path):
                    os.unlink(temp_input_path)
                if os.path.exists(temp_output_path):
                    os.unlink(temp_output_path)
                    
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            await message.reply(get_translation(user_language, "processing_error"))
            await self.log_request(user_id, 'colorize', success=False, error_message=str(e))
            self.performance_monitor.record_error()
        finally:
            self.performance_monitor.decrement_request()
    
    async def handle_text(self, message: Message):
        """Handle text messages"""
        user_language = await self.get_user_language(message.from_user.id)
        await message.reply(get_translation(user_language, "send_image"))
        await self.log_request(message.from_user.id, 'text_message')
    
    async def error_handler(self, update: types.Update, exception: Exception):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {exception}")
        
        if isinstance(update, types.Message) and update.text:
            user_language = await self.get_user_language(update.from_user.id)
            await update.reply(get_translation(user_language, "error_occurred"))
    
    async def start_polling(self):
        """Start the bot"""
        try:
            await self.init_services()
            logger.info("🤖 Starting Image Colorization Bot...")
            logger.info(f"📁 Model path: {MODEL_PATH}")
            logger.info(f"📁 Prototxt path: {PROTOTXT_PATH}")
            logger.info("✅ Bot is running! Press Ctrl+C to stop.")
            
            await self.dp.start_polling(self.bot)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
        finally:
            await self.close_services()

async def main():
    """Main function"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set your BOT_TOKEN in config.py or as an environment variable.")
        print("Get your bot token from @BotFather on Telegram.")
        return
    
    bot = ColorizationBot()
    await bot.start_polling()

if __name__ == '__main__':
    asyncio.run(main())