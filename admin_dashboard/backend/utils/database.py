"""
MongoDB Database Connection and Utilities
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB Database Manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(
                settings.mongodb_url,
                server_api=ServerApi('1')
            )
            # Test connection
            await cls.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        """Get database instance"""
        if not cls.client:
            raise Exception("Database not connected. Call connect_db() first.")
        return cls.client[settings.database_name]


# Database instance getter
def get_db():
    """Dependency for getting database instance"""
    return Database.get_database()


# Initialize default users and collections
async def init_database():
    """Initialize database with default data"""
    from models.user import User, UserRole
    from passlib.context import CryptContext
    from datetime import datetime
    
    pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        deprecated="auto"
    )
    db = get_db()
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.job_postings.create_index("created_at")
    await db.candidates.create_index([("job_posting_id", 1), ("email", 1)], unique=True)
    await db.interviews.create_index("candidate_id")
    
    # Create default users if they don't exist
    default_users = [
        {
            "email": "admin@admin.com",
            "full_name": "Super Admin",
            "role": UserRole.SUPER_ADMIN,
            "password": "password123"
        },
        {
            "email": "hr@admin.com",
            "full_name": "HR Manager",
            "role": UserRole.HR_MANAGER,
            "password": "password123"
        },
        {
            "email": "interviewer@admin.com",
            "full_name": "Interviewer",
            "role": UserRole.INTERVIEWER,
            "password": "password123"
        }
    ]
    
    for user_data in default_users:
        existing = await db.users.find_one({"email": user_data["email"]})
        if not existing:
            password = user_data.pop("password")
            hashed_password = pwd_context.hash(password)
            user_doc = {
                **user_data,
                "hashed_password": hashed_password,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            await db.users.insert_one(user_doc)
            logger.info(f"✅ Created default user: {user_data['email']}")
    
    logger.info("✅ Database initialization complete")
