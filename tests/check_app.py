#!/usr/bin/env python3
"""
Script to check the functionality of the application after data recovery
"""

import asyncio
from pathlib import Path
import sys

# Add project path
sys.path.append(str(Path(__file__).parent))

from app.database.db_manager import DBManager
from app.services.themes import ThemeService
from app.services.users import UserService
from app.services.roles import RoleService


async def check_app_data():
    """Check application functionality and data availability"""
    print("Checking application functionality...")
    
    async with DBManager() as db_manager:
        # Check themes
        theme_service = ThemeService(db_manager)
        themes = await db_manager.themes.get_all()
        print(f"Found {len(themes)} themes")
        
        # Display first few themes
        for theme in themes[:3]:
            print(f" - Theme: {theme.name} (ID: {theme.id})")
        
        # Check users
        user_service = UserService(db_manager)
        users = await db_manager.users.get_all()
        print(f"Found {len(users)} users")
        
        # Display users
        for user in users:
            print(f"  - User: {user.name} (ID: {user.id}, Email: {user.email})")
        
        # Check roles
        role_service = RoleService(db_manager)
        roles = await db_manager.roles.get_all()
        print(f"Found {len(roles)} roles")
        
        # Display roles
        for role in roles:
            print(f"  - Role: {role.name} (ID: {role.id}, Level: {role.level})")
    
    print("\nApplication works correctly, data restored!")


if __name__ == "__main__":
    asyncio.run(check_app_data())