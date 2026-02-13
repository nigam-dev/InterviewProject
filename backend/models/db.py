from sqlalchemy import Column, Integer, String, Float
from core.database import Base

class Player(Base):
    """Player model for database"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    runs = Column(Integer, nullable=False)
    wickets = Column(Integer, nullable=False)
    strike_rate = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    role = Column(String(10), nullable=False)
    
    def __repr__(self):
        return f"<Player(name='{self.name}', role='{self.role}', price={self.price})>"
