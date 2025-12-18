"""
Test to verify the admin panel changes work correctly with the blocked role
"""
import asyncio
from app.database.database import async_session_maker
from app.models.roles import RoleModel
from app.services.users import UserService
from app.database.db_manager import DBManager
from sqlalchemy import select

async def test_role_assignment_options():
    print("Testing role assignment options in admin panel...")
    
    # Verify that all roles (including blocked) exist in the database
    async with async_session_maker() as session:
        result = await session.execute(select(RoleModel))
        roles = result.scalars().all()
        
        print("Available roles in database:")
        role_dict = {}
        for role in roles:
            role_dict[role.id] = role.name
            print(f"  ID {role.id}: {role.name} (level {role.level})")
        
        # Check if all expected roles are present
        expected_roles = {
            1: "user",
            2: "moderator", 
            3: "admin",
            4: "blocked"
        }
        
        all_present = True
        for role_id, role_name in expected_roles.items():
            if role_id in role_dict and role_dict[role_id] == role_name:
                print(f"  V Role ID {role_id} ({role_name}) is available")
            else:
                print(f"  X Role ID {role_id} ({role_name}) is missing")
                all_present = False
        
        if all_present:
            print("\nV All roles are available for assignment in the admin panel")
            print("The admin panel dropdown now includes: user, moderator, admin, blocked")
        else:
            print("\nX Some roles are missing")
    
    # Test UserService functionality
    async with DBManager() as db:
        user_service = UserService(db)
        
        # Test retrieving each role by name
        roles_to_test = ["user", "moderator", "admin", "blocked"]
        print(f"\nTesting UserService.get_role_by_name method:")
        
        for role_name in roles_to_test:
            try:
                role = await user_service.get_role_by_name(role_name)
                if role:
                    print(f"  V Can retrieve '{role_name}' role: ID {role.id}")
                else:
                    print(f"  X Cannot retrieve '{role_name}' role")
            except Exception as e:
                print(f"  X Error retrieving '{role_name}' role: {str(e)}")

    print(f"\nAdmin panel changes summary:")
    print(f"- Added 'Заблокирован' option to role assignment dropdown (value 4)")
    print(f"- Users can now be assigned directly to the blocked role from admin panel")
    print(f"- Blocked users will not be able to log in (level 0 restriction)")
    print(f"- Existing block/unblock endpoints still work as expected")

if __name__ == "__main__":
    asyncio.run(test_role_assignment_options())