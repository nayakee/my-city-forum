from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.database import Base
 
user_communities = Table(
    'user_communities',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('community_id', Integer, ForeignKey('communities.id'), primary_key=True),
)