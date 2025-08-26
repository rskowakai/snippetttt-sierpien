from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class PismoStatus(str, enum.Enum):
    NOWE = 'NOWE'
    W_ANALIZIE = 'W ANALIZIE'
    OCZEKUJE_NA_DECYZJE = 'OCZEKUJE_NA_DECYZJE'
    REALIZOWANE = 'REALIZOWANE'
    ZAKONCZONE = 'ZAKOŃCZONE'
    ANULOWANE = 'ANULOWANE'

class Pismo(Base):
    __tablename__ = 'pisma'
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(PismoStatus), default=PismoStatus.NOWE, nullable=False)
    user_comments = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    owner = relationship('User')
    analizy = relationship('Analiza', back_populates='pismo')
