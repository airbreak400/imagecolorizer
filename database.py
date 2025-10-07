import asyncio
import asyncpg
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True, default='en')
    is_bot = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    total_requests = Column(Integer, default=0)
    total_images_processed = Column(Integer, default=0)
    is_blocked = Column(Boolean, default=False)
    extra_data = Column(JSONB, default={})  # Renamed from metadata

class Request(Base):
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    request_type = Column(String(50), nullable=False)  # 'colorize', 'start', 'help', etc.
    file_id = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)  # in seconds
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSONB, default={})  # Renamed from metadata

class Statistics(Base):
    __tablename__ = 'statistics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    total_processing_time = Column(Float, default=0.0)
    average_processing_time = Column(Float, default=0.0)
    extra_data = Column(JSONB, default={})  # Renamed from metadata

class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.pool = None
    
    async def init_database(self, min_size: int = 50, max_size: int = 200):
        """Initialize database connection and create tables"""
        try:
            # Create SQLAlchemy engine
            self.engine = create_engine(self.database_url, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create asyncpg pool for async operations with optimized settings
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=30,
                server_settings={
                    'application_name': 'colorization_bot',
                    'jit': 'off'  # Disable JIT for better performance
                }
            )
            
            logger.info(f"Database initialized successfully with pool size {min_size}-{max_size}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
        if self.engine:
            self.engine.dispose()
    
    async def get_or_create_user(self, telegram_id: int, username: str = None, 
                               first_name: str = None, last_name: str = None,
                               language_code: str = 'en', is_premium: bool = False) -> User:
        """Get or create user in database"""
        async with self.pool.acquire() as conn:
            # Check if user exists
            user_data = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1", telegram_id
            )
            
            if user_data:
                # Update last activity and user info
                await conn.execute(
                    "UPDATE users SET last_activity = $1, username = $2, first_name = $3, last_name = $4, is_premium = $5, language_code = $6 WHERE telegram_id = $7",
                    datetime.utcnow(), username, first_name, last_name, is_premium, language_code, telegram_id
                )
                return User(**dict(user_data))
            else:
                # Create new user
                await conn.execute(
                    """INSERT INTO users (telegram_id, username, first_name, last_name, language_code, is_premium, created_at, last_activity)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                    telegram_id, username, first_name, last_name, language_code, is_premium, datetime.utcnow(), datetime.utcnow()
                )
                
                # Get the created user
                user_data = await conn.fetchrow(
                    "SELECT * FROM users WHERE telegram_id = $1", telegram_id
                )
                return User(**dict(user_data))
    
    async def log_request(self, user_id: int, request_type: str, file_id: str = None,
                         file_size: int = None, processing_time: float = None,
                         success: bool = True, error_message: str = None,
                         extra_data: Dict[str, Any] = None):  # Renamed parameter
        """Log a user request"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO requests (user_id, request_type, file_id, file_size, processing_time, success, error_message, created_at, extra_data)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)""",
                user_id, request_type, file_id, file_size, processing_time, success, error_message, datetime.utcnow(), json.dumps(extra_data or {})
            )
            
            # Update user statistics
            if success and request_type == 'colorize':
                await conn.execute(
                    "UPDATE users SET total_requests = total_requests + 1, total_images_processed = total_images_processed + 1 WHERE telegram_id = $1",
                    user_id
                )
            else:
                await conn.execute(
                    "UPDATE users SET total_requests = total_requests + 1 WHERE telegram_id = $1",
                    user_id
                )
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        async with self.pool.acquire() as conn:
            user_data = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1", user_id
            )
            
            if not user_data:
                return {}
            
            # Get recent requests
            recent_requests = await conn.fetch(
                "SELECT * FROM requests WHERE user_id = $1 ORDER BY created_at DESC LIMIT 10",
                user_id
            )
            
            return {
                'user': dict(user_data),
                'recent_requests': [dict(req) for req in recent_requests]
            }
    
    async def get_global_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get global statistics"""
        async with self.pool.acquire() as conn:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Total users
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            
            # Active users (last 7 days)
            active_users = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE last_activity >= $1",
                datetime.utcnow() - timedelta(days=7)
            )
            
            # Total requests
            total_requests = await conn.fetchval(
                "SELECT COUNT(*) FROM requests WHERE created_at >= $1",
                since_date
            )
            
            # Successful requests
            successful_requests = await conn.fetchval(
                "SELECT COUNT(*) FROM requests WHERE success = true AND created_at >= $1",
                since_date
            )
            
            # Failed requests
            failed_requests = await conn.fetchval(
                "SELECT COUNT(*) FROM requests WHERE success = false AND created_at >= $1",
                since_date
            )
            
            # Average processing time
            avg_processing_time = await conn.fetchval(
                "SELECT AVG(processing_time) FROM requests WHERE processing_time IS NOT NULL AND created_at >= $1",
                since_date
            )
            
            # Requests by type
            requests_by_type = await conn.fetch(
                "SELECT request_type, COUNT(*) as count FROM requests WHERE created_at >= $1 GROUP BY request_type",
                since_date
            )
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                'average_processing_time': avg_processing_time or 0,
                'requests_by_type': {row['request_type']: row['count'] for row in requests_by_type}
            }
    
    async def cleanup_old_data(self, days: int = 365):
        """Clean up old data"""
        async with self.pool.acquire() as conn:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old requests
            deleted_requests = await conn.execute(
                "DELETE FROM requests WHERE created_at < $1",
                cutoff_date
            )
            
            logger.info(f"Cleaned up {deleted_requests} old requests")
    
    async def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by activity"""
        async with self.pool.acquire() as conn:
            top_users = await conn.fetch(
                """SELECT telegram_id, username, first_name, total_requests, total_images_processed, last_activity
                   FROM users 
                   ORDER BY total_requests DESC 
                   LIMIT $1""",
                limit
            )
            
            return [dict(user) for user in top_users]
    
    async def update_user_language(self, user_id: int, language_code: str):
        """Update user's language preference"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET language_code = $1 WHERE telegram_id = $2",
                language_code, user_id
            )
    
    async def get_user_language(self, user_id: int) -> str:
        """Get user's language preference"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT language_code FROM users WHERE telegram_id = $1",
                user_id
            )
            return result or 'en'