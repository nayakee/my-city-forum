from app.models.user_communities import UserCommunityModel
from app.repositories.base import BaseRepository
from app.schemes.user_communities import SUserCommunityGet


class UserCommunitiesRepository(BaseRepository):
    """Репозиторий для работы с ассоциациями пользователей и сообществ"""
    
    model = UserCommunityModel
    schema = SUserCommunityGet
    
    def __init__(self, session):
        self.session = session