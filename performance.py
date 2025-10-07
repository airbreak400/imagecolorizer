"""
Performance optimization module for high-load scenarios
"""
import asyncio
import logging
import hashlib
import os
import gc
import psutil
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import aiofiles
import redis.asyncio as redis
import asyncpg

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and bot metrics"""
    
    def __init__(self):
        self.request_count = 0
        self.active_requests = 0
        self.max_concurrent_requests = 0
        self.start_time = datetime.utcnow()
        self.processing_times = []
        self.error_count = 0
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'active_requests': self.active_requests,
            'total_requests': self.request_count,
            'max_concurrent': self.max_concurrent_requests,
            'uptime_hours': (datetime.utcnow() - self.start_time).total_seconds() / 3600,
            'avg_processing_time': sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
            'error_rate': self.error_count / max(self.request_count, 1)
        }
    
    def increment_request(self):
        """Increment request counter"""
        self.request_count += 1
        self.active_requests += 1
        self.max_concurrent_requests = max(self.max_concurrent_requests, self.active_requests)
    
    def decrement_request(self):
        """Decrement active request counter"""
        self.active_requests = max(0, self.active_requests - 1)
    
    def record_processing_time(self, processing_time: float):
        """Record processing time for statistics"""
        self.processing_times.append(processing_time)
        # Keep only last 1000 processing times
        if len(self.processing_times) > 1000:
            self.processing_times = self.processing_times[-1000:]
    
    def record_error(self):
        """Record an error"""
        self.error_count += 1

class ImageCache:
    """Cache for processed images to avoid reprocessing"""
    
    def __init__(self, redis_client, ttl: int = 86400):
        self.redis = redis_client
        self.ttl = ttl
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _get_image_hash(self, image_path: str) -> str:
        """Generate hash for image file"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating image hash: {e}")
            return hashlib.md5(str(time.time()).encode()).hexdigest()
    
    async def get_cached_result(self, image_path: str) -> Optional[bytes]:
        """Get cached colorized image"""
        try:
            image_hash = self._get_image_hash(image_path)
            cache_key = f"colorized:{image_hash}"
            result = await self.redis.get(cache_key)
            
            if result:
                self.cache_hits += 1
                logger.info(f"Cache hit for image {image_hash[:8]}...")
                return result
            else:
                self.cache_misses += 1
                return None
        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            return None
    
    async def cache_result(self, image_path: str, result_bytes: bytes):
        """Cache colorized image result"""
        try:
            image_hash = self._get_image_hash(image_path)
            cache_key = f"colorized:{image_hash}"
            await self.redis.setex(cache_key, self.ttl, result_bytes)
            logger.info(f"Cached result for image {image_hash[:8]}...")
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }

class AsyncImageProcessor:
    """Async image processing with thread pool"""
    
    def __init__(self, max_workers: int = 20):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = 0
        self.max_active_tasks = 0
    
    async def process_image_async(self, process_func, *args, **kwargs):
        """Process image in thread pool to avoid blocking"""
        try:
            self.active_tasks += 1
            self.max_active_tasks = max(self.max_active_tasks, self.active_tasks)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, process_func, *args, **kwargs)
            
            self.active_tasks -= 1
            return result
        except Exception as e:
            self.active_tasks -= 1
            logger.error(f"Error in async image processing: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        return {
            'active_tasks': self.active_tasks,
            'max_active_tasks': self.max_active_tasks,
            'max_workers': self.executor._max_workers
        }
    
    def shutdown(self):
        """Shutdown thread pool"""
        self.executor.shutdown(wait=True)

class ResourceManager:
    """Manage system resources and cleanup"""
    
    def __init__(self, memory_limit_mb: int = 2048):
        self.temp_files = set()
        self.cleanup_interval = 300  # 5 minutes
        self.memory_limit_mb = memory_limit_mb
        self.last_cleanup = datetime.utcnow()
    
    def register_temp_file(self, file_path: str):
        """Register temporary file for cleanup"""
        self.temp_files.add(file_path)
    
    def unregister_temp_file(self, file_path: str):
        """Unregister temporary file"""
        self.temp_files.discard(file_path)
    
    async def cleanup_temp_files(self):
        """Clean up temporary files"""
        cleaned_count = 0
        for file_path in list(self.temp_files):
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    cleaned_count += 1
                self.temp_files.discard(file_path)
            except Exception as e:
                logger.error(f"Error cleaning up {file_path}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} temporary files")
    
    def check_memory_usage(self) -> bool:
        """Check if memory usage is within limits"""
        memory_mb = psutil.virtual_memory().used / (1024 * 1024)
        return memory_mb < self.memory_limit_mb
    
    async def force_cleanup(self):
        """Force cleanup of resources"""
        await self.cleanup_temp_files()
        gc.collect()  # Force garbage collection
        logger.info("Forced cleanup completed")
    
    async def periodic_cleanup(self):
        """Periodic cleanup of resources"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Check if cleanup is needed
                if not self.check_memory_usage():
                    logger.warning("Memory usage high, forcing cleanup")
                    await self.force_cleanup()
                else:
                    await self.cleanup_temp_files()
                
                self.last_cleanup = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")

class LoadBalancer:
    """Simple load balancer for handling high concurrent requests"""
    
    def __init__(self, max_concurrent: int = 100):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue = asyncio.Queue(maxsize=1000)
        self.workers = []
        self.active_requests = 0
    
    async def process_request(self, request_func, *args, **kwargs):
        """Process request with load balancing"""
        async with self.semaphore:
            self.active_requests += 1
            try:
                result = await request_func(*args, **kwargs)
                return result
            finally:
                self.active_requests -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        return {
            'active_requests': self.active_requests,
            'max_concurrent': self.max_concurrent,
            'queue_size': self.queue.qsize(),
            'semaphore_value': self.semaphore._value
        }

class HealthChecker:
    """Health check system for monitoring bot status"""
    
    def __init__(self, db_manager, redis_client, model_loader):
        self.db = db_manager
        self.redis = redis_client
        self.model = model_loader
        self.last_health_check = None
        self.health_status = "unknown"
    
    async def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        # Check database
        try:
            if self.db and self.db.pool:
                async with self.db.pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health_status['components']['database'] = 'healthy'
            else:
                health_status['components']['database'] = 'unhealthy: no connection'
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['database'] = f'unhealthy: {str(e)}'
            health_status['overall_status'] = 'degraded'
        
        # Check Redis
        try:
            await self.redis.ping()
            health_status['components']['redis'] = 'healthy'
        except Exception as e:
            health_status['components']['redis'] = f'unhealthy: {str(e)}'
            health_status['overall_status'] = 'degraded'
        
        # Check model
        try:
            if self.model and hasattr(self.model, 'net') and self.model.net:
                health_status['components']['model'] = 'healthy'
            else:
                health_status['components']['model'] = 'unhealthy: model not loaded'
                health_status['overall_status'] = 'degraded'
        except Exception as e:
            health_status['components']['model'] = f'unhealthy: {str(e)}'
            health_status['overall_status'] = 'degraded'
        
        # Check system resources
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        health_status['components']['system'] = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'status': 'healthy' if cpu_percent < 90 and memory_percent < 90 else 'warning'
        }
        
        if cpu_percent > 95 or memory_percent > 95:
            health_status['overall_status'] = 'critical'
        
        self.last_health_check = health_status
        self.health_status = health_status['overall_status']
        return health_status
    
    async def start_health_monitoring(self, interval: int = 60):
        """Start periodic health monitoring"""
        while True:
            try:
                health = await self.check_health()
                if health['overall_status'] != 'healthy':
                    logger.warning(f"Health check failed: {health}")
            except Exception as e:
                logger.error(f"Health check error: {e}")
            
            await asyncio.sleep(interval)

class MetricsCollector:
    """Collect and analyze bot performance metrics"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.metrics_key = "bot:metrics"
    
    async def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric"""
        try:
            timestamp = datetime.utcnow().isoformat()
            metric_data = {
                'name': metric_name,
                'value': value,
                'timestamp': timestamp,
                'tags': tags or {}
            }
            
            import json
            await self.redis.lpush(self.metrics_key, json.dumps(metric_data))
            await self.redis.ltrim(self.metrics_key, 0, 10000)  # Keep last 10k metrics
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
    
    async def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            metrics = await self.redis.lrange(self.metrics_key, 0, -1)
            
            recent_metrics = []
            for metric_str in metrics:
                try:
                    import json
                    metric = json.loads(metric_str)  # Safe JSON parsing instead of eval
                    if datetime.fromisoformat(metric['timestamp']) > cutoff_time:
                        recent_metrics.append(metric)
                except:
                    continue
            
            # Calculate summary statistics
            if not recent_metrics:
                return {}
            
            processing_times = [m['value'] for m in recent_metrics if m['name'] == 'processing_time']
            request_counts = [m['value'] for m in recent_metrics if m['name'] == 'request_count']
            
            return {
                'avg_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0,
                'max_processing_time': max(processing_times) if processing_times else 0,
                'total_requests': sum(request_counts) if request_counts else 0,
                'metrics_count': len(recent_metrics)
            }
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}

class OptimizedConnectionPool:
    """Optimized connection pool for database and Redis"""
    
    def __init__(self, db_url: str, redis_url: str):
        self.db_url = db_url
        self.redis_url = redis_url
        self.db_pool = None
        self.redis_pool = None
    
    async def init_pools(self, min_size: int = 50, max_size: int = 200):
        """Initialize connection pools with optimal settings"""
        try:
            # Database pool with more connections for high load
            self.db_pool = await asyncpg.create_pool(
                self.db_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=30,
                server_settings={
                    'application_name': 'colorization_bot',
                    'jit': 'off'  # Disable JIT for better performance
                }
            )
            
            # Redis pool with connection pooling
            self.redis_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=100,
                retry_on_timeout=True
            )
            
            logger.info(f"Connection pools initialized: DB({min_size}-{max_size}), Redis(100)")
            
        except Exception as e:
            logger.error(f"Error initializing connection pools: {e}")
            raise
    
    async def close_pools(self):
        """Close all connection pools"""
        try:
            if self.db_pool:
                await self.db_pool.close()
            if self.redis_pool:
                await self.redis_pool.disconnect()
            logger.info("Connection pools closed")
        except Exception as e:
            logger.error(f"Error closing connection pools: {e}")


