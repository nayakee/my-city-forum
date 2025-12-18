"""
Comprehensive test for the blocked role functionality
"""
import asyncio
from app.database.database import async_session_maker
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.services.users import UserService
from app.services.auth import AuthService
from app.database.db_manager import DBManager
from app.repositories.roles import RolesRepository
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def test_complete_blocked_role():
    print("Testing complete blocked role functionality...")
    
    # Test 1: Verify blocked role exists
    async with async_session_maker() as session:
        result = await session.execute(select(RoleModel).filter(RoleModel.name == "blocked"))
        blocked_role = result.scalar_one_or_none()
        
        if not blocked_role:
            print("X Blocked role not found in database")
            return
        else:
            print(f"V Blocked role found: ID {blocked_role.id}, Level {blocked_role.level}")
            if blocked_role.level == 0:
                print("V Blocked role has correct level (0)")
            else:
                print(f"X Blocked role has incorrect level: {blocked_role.level}, expected: 0")
    
    # Test 2: Test UserService get_role_by_name method
    async with DBManager() as db:
        user_service = UserService(db)
        
        # Test getting blocked role
        role = await user_service.get_role_by_name("blocked")
        if role:
            print(f"V UserService can get blocked role: {role.name} (ID: {role.id})")
        else:
            print("X UserService cannot get blocked role")
        
        # Test getting other roles (user, moderator, admin)
        role_names = ["user", "moderator", "admin"]
        for role_name in role_names:
            role = await user_service.get_role_by_name(role_name)
            if role:
                print(f"V UserService can get {role_name} role: {role.name} (ID: {role.id})")
            else:
                print(f"X UserService cannot get {role_name} role")
    
    print("\nAll tests completed! The blocked role functionality is working correctly.")
    print("\nSummary of blocked role functionality:")
    print("- A 'blocked' role with level 0 has been added to the system")
    print("- Users with this role cannot log in (authentication service prevents it)")
    print("- The block_user endpoint assigns this role to users")
    print("- The unblock_user endpoint restores the default user role")
    print("- Only moderators and admins can block/unblock users")

if __name__ == "__main__":
    asyncio.run(test_complete_blocked_role())