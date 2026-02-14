"""
User Management Utility Script
Verify and manage users in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

# Configuration
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "hr_recruitment_db"

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


async def list_users():
    """List all users in the database"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("\n" + "="*60)
    print("CURRENT USERS IN DATABASE")
    print("="*60)
    
    cursor = db.users.find({})
    count = 0
    async for user in cursor:
        count += 1
        print(f"\n{count}. {user['full_name']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        print(f"   Active: {user.get('is_active', True)}")
        print(f"   Created: {user.get('created_at', 'N/A')}")
    
    if count == 0:
        print("\n⚠️  No users found in database!")
    else:
        print(f"\n✅ Total users: {count}")
    
    print("="*60 + "\n")
    client.close()


async def verify_user(email: str, password: str):
    """Verify if a user can login"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print(f"\n🔍 Verifying user: {email}")
    
    user = await db.users.find_one({"email": email})
    
    if not user:
        print(f"❌ User not found: {email}")
        client.close()
        return False
    
    print(f"✅ User found: {user['full_name']}")
    print(f"   Role: {user['role']}")
    
    # Verify password
    if pwd_context.verify(password, user['hashed_password']):
        print(f"✅ Password verification: SUCCESS")
        client.close()
        return True
    else:
        print(f"❌ Password verification: FAILED")
        client.close()
        return False


async def reset_password(email: str, new_password: str):
    """Reset a user's password"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print(f"\n🔄 Resetting password for: {email}")
    
    user = await db.users.find_one({"email": email})
    
    if not user:
        print(f"❌ User not found: {email}")
        client.close()
        return
    
    hashed_password = pwd_context.hash(new_password)
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    print(f"✅ Password reset successfully!")
    print(f"   New password: {new_password}")
    
    client.close()


async def create_default_users():
    """Create all default users"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("\n🚀 Creating default users...")
    
    default_users = [
        {
            "email": "admin@admin.com",
            "full_name": "Super Admin",
            "role": "SUPER_ADMIN",
            "password": "password123"
        },
        {
            "email": "hr@admin.com",
            "full_name": "HR Manager",
            "role": "HR_MANAGER",
            "password": "password123"
        },
        {
            "email": "interviewer@admin.com",
            "full_name": "Interviewer",
            "role": "INTERVIEWER",
            "password": "password123"
        }
    ]
    
    for user_data in default_users:
        email = user_data["email"]
        existing = await db.users.find_one({"email": email})
        
        if existing:
            print(f"⚠️  User already exists: {email}")
            continue
        
        password = user_data.pop("password")
        hashed_password = pwd_context.hash(password)
        
        user_doc = {
            **user_data,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user_doc)
        print(f"✅ Created user: {email}")
    
    print("\n✅ Default users creation complete!")
    client.close()


async def delete_all_users():
    """Delete all users (DANGER!)"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("\n⚠️  WARNING: This will DELETE ALL USERS!")
    confirm = input("Type 'DELETE ALL' to confirm: ")
    
    if confirm != "DELETE ALL":
        print("❌ Cancelled")
        client.close()
        return
    
    result = await db.users.delete_many({})
    print(f"✅ Deleted {result.deleted_count} users")
    
    client.close()


async def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("USER MANAGEMENT UTILITY")
        print("="*60)
        print("1. List all users")
        print("2. Verify user login")
        print("3. Reset user password")
        print("4. Create default users")
        print("5. Delete all users (DANGER!)")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            await list_users()
        
        elif choice == "2":
            email = input("Enter email: ").strip()
            password = input("Enter password: ").strip()
            await verify_user(email, password)
        
        elif choice == "3":
            email = input("Enter email: ").strip()
            new_password = input("Enter new password: ").strip()
            await reset_password(email, new_password)
        
        elif choice == "4":
            await create_default_users()
        
        elif choice == "5":
            await delete_all_users()
        
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    print("HR Recruitment System - User Management Utility")
    asyncio.run(main())
