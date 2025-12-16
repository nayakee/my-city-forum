from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.communities import CommunityModel
 
class UserCommunityModel(Base):
    __tablename__ = "user_communities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), nullable=False)
    
    user: Mapped["UserModel"] = relationship(back_populates="community_associations", overlaps="communities,users")
    community: Mapped["CommunityModel"] = relationship(back_populates="user_associations", overlaps="users,communities")
