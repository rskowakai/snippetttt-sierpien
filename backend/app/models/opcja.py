from sqlalchemy import Column, Integer, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Opcja(Base):
    __tablename__ = 'opcje'
    id = Column(Integer, primary_key=True, index=True)
    analiza_id = Column(Integer, ForeignKey('analizy.id'), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    is_purchased = Column(Boolean, default=False, nullable=False)
    realization_details = Column(Text, nullable=True)

    analiza = relationship('Analiza', back_populates='opcje')
