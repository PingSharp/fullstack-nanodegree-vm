import sys
from sqlalchemy import Column, ForeignKey,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
class Restaurant(Base):
    __tablename__ = 'restaurant'
    name = Column(
        String(80),nullable = False)
    id = Column(
        Integer,primary_key = True
    )
    menuitem = relationship("MenuItem",back_populates='restaurant',cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Restaurant(name='%s')>"%self.name
    

class MenuItem(Base):
    __tablename__ = 'menuitem'
    name = Column(String(80),nullable = False)
    id = Column(Integer,primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    Restaurant_id = Column(
        Integer,ForeignKey('restaurant.id')
    )
    restaurant = relationship("Restaurant",back_populates="menuitem")

    def __repr__(self):
        return "<MenuItem(name='%s',course='%s',description='%s',price='%s')>"%(self.name,self.course,self.description,self.price)
engine = create_engine(
    'sqlite:///restaurantmenu.db'
)

Base.metadata.create_all(engine)