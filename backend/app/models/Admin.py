from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Admin(Base):
    __tablename__ = "admin"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
