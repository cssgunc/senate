from .base import Base
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

class Admin(Base):
    __tablename__ = "admin"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
