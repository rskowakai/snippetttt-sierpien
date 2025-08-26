from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Analiza(Base):
    __tablename__ = 'analizy'
    id = Column(Integer, primary_key=True, index=True)
    pismo_id = Column(Integer, ForeignKey('pisma.id'), nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    summary = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)  # lista linków

    pismo = relationship('Pismo', back_populates='analizy')
    opcje = relationship('Opcja', back_populates='analiza')
