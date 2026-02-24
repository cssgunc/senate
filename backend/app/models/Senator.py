from .base import Base
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

class Senator(Base):
    __tablename__ = "senator"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
