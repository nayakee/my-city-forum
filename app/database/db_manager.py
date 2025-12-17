from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.repositories.users import UsersRepository
from app.repositories.roles import RolesRepository
from app.repositories.posts import PostsRepository
from app.repositories.comments import CommentsRepository
from app.repositories.communities import CommunitiesRepository
from app.repositories.reports import ReportsRepository
from app.repositories.themes import ThemesRepository
from app.repositories.user_communities import UserCommunitiesRepository


class DBManager:
    """Менеджер для работы с базой данных и репозиториями"""
    
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory
        self.session: Optional[AsyncSession] = None
        
        # Репозитории будут инициализированы при входе в контекст
        self.users: Optional[UsersRepository] = None
        self.roles: Optional[RolesRepository] = None
        self.posts: Optional[PostsRepository] = None
        self.comments: Optional[CommentsRepository] = None
        self.communities: Optional[CommunitiesRepository] = None
        self.reports: Optional[ReportsRepository] = None
        self.themes: Optional[ThemesRepository] = None
        self.user_communities: Optional[UserCommunitiesRepository] = None

    async def __aenter__(self):
        """Вход в контекстный менеджер"""
        self.session = self.session_factory()
        
        # Инициализируем все репозитории
        self.users = UsersRepository(self.session)
        self.roles = RolesRepository(self.session)
        self.posts = PostsRepository(self.session)
        self.comments = CommentsRepository(self.session)
        self.communities = CommunitiesRepository(self.session)
        self.reports = ReportsRepository(self.session)
        self.themes = ThemesRepository(self.session)
        self.user_communities = UserCommunitiesRepository(self.session)
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера"""
        if exc_type is not None:
            # Если была ошибка - откатываем транзакцию
            await self.session.rollback()
        else:
            # Если все хорошо - коммитим
            await self.session.commit()
        
        await self.session.close()
        
        # Очищаем ссылки на репозитории
        self.users = None
        self.roles = None
        self.posts = None
        self.comments = None
        self.communities = None
        self.reports = None
        self.themes = None
        self.user_communities = None
        self.session = None

    async def commit(self):
        """Явный коммит транзакции"""
        if self.session:
            await self.session.commit()

    async def rollback(self):
        """Откат транзакции"""
        if self.session:
            await self.session.rollback()

    def get_repository(self, repository_type):
        """Получение репозитория по типу"""
        repositories = {
            'users': self.users,
            'roles': self.roles,
            'posts': self.posts,
            'comments': self.comments,
            'communities': self.communities,
            'reports': self.reports,
            'themes': self.themes,
            'user_communities': self.user_communities,
        }
        
        return repositories.get(repository_type)