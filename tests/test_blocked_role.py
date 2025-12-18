"""
Test script to verify the blocked role functionality
"""
import asyncio
from app.database.database import async_session_maker
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.services.users import UserService
from app.services.auth import AuthService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.db_manager import DBManager
from app.repositories.roles import RolesRepository

async def test_blocked_role():
    print("Testing blocked role functionality...")
    
    async with async_session_maker() as session:
        # Get the blocked role
        result = await session.execute(select(RoleModel).filter(RoleModel.name == "blocked"))
        blocked_role = result.scalar_one_or_none()
        
        if not blocked_role:
            print("X Blocked role not found in database")
            return
        else:
            print(f"V Blocked role found: ID {blocked_role.id}, Level {blocked_role.level}")
    
    # Test UserService methods
    async with async_session_maker() as session:
        from app.database.db_manager import DBManager
        db_manager = DBManager()
        db_manager.session = session
        db_manager.roles = RolesRepository(session)
        
        user_service = UserService(db_manager)
        
        # Test getting role by name
        role = await user_service.get_role_by_name("blocked")
        if role:
            print(f"V UserService can get blocked role: {role.name} (ID: {role.id})")
        else:
            print("X UserService cannot get blocked role")
        
        # Test getting user role by name
        user_role = await user_service.get_role_by_name("user")
        if user_role:
            print(f"V UserService can get user role: {user_role.name} (ID: {user_role.id})")
        else:
            print("X UserService cannot get user role")

    print("\nTesting blocked role functionality completed!")

if __name__ == "__main__":
    asyncio.run(test_blocked_role())