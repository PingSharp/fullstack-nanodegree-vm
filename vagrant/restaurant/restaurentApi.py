from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Restaurant, Base, MenuItem
 
engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
session = DBSession()

def getAllRestaurants():
    restaurants = session.query(Restaurant)
    return restaurants
def getRestaurantById(rid):
    restaurant = session.query(Restaurant).filter_by(id=rid).one()
    return restaurant
def deleteRestaurant(rid):
    deleteObj = session.query(Restaurant).filter_by(id=rid).one()
    session.delete(deleteObj)
    session.commit()
def addNewRestaurant(rname):
    restaurant1 = Restaurant(name = rname[0])
    session.add(restaurant1)
    session.commit()
def changeNameOfRestaurant(rid,rname):
    restaurant = session.query(Restaurant).filter_by(id=rid).first()
    restaurant.name = rname[0]
    session.commit()