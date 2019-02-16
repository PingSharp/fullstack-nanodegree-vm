from flask import Flask
from flask import (render_template,request)
app = Flask(__name__)
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
 
from database_setup import Restaurant, Base, MenuItem
 
engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
session = scoped_session(sessionmaker(bind=engine))



def getAllRestaurants():
    restaurants = session.query(Restaurant)
    return restaurants
def getRestaurantById(rid):
    restaurant = restaurants.filter_by(id=rid).one()
    return restaurant
def deleteRestaurant(rid):
    deleteObj = restaurants.filter_by(id=rid).one()
    session.delete(deleteObj)
    session.commit()
def deleteMenuItemdb(mid):
    deleteItem = session.query(MenuItem).filter_by(id=mid).one()
    session.delete(deleteItem)
    session.commit()
def addNewRestaurant(rname):
    restaurant1 = Restaurant(name = rname[0])
    session.add(restaurant1)
    session.commit()
def changeNameOfRestaurant(rid,rname):
    restaurant = restaurants.filter_by(id=rid).first()
    restaurant.name = rname[0]
    session.commit()
def changeMenuItem(mid,nName,nCourse,nDes,nPrice):
    item = session.query(MenuItem).filter_by(id=mid).first()
    item.name = nName[0]
    item.course = nCourse[0]
    item.description = nDes[0]
    item.price = nPrice[0]
    session.commit()

def getMenuItems(rid):
    menuitems = session.query(MenuItem).filter_by(Restaurant_id = rid)
    return menuitems
def addNewMenuItem(rname,rcourse,rdes,rprice,rid):
    newMenuItem = MenuItem(name=rname[0],course=rcourse[0],description=rdes[0],price=rprice[0],Restaurant_id=rid)
    session.add(newMenuItem)
    session.commit()
def getMenuItem(rid,mid):
    menuitems = session.query(MenuItem).filter_by(Restaurant_id = rid)
    menuitem = menuitems.filter_by(id=mid)
    mi = menuitem.one()
    return mi


@app.route('/')
@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    
    menuitems = session.query(MenuItem).filter_by(Restaurant_id = restaurant_id)
    
    output = ""
    for item in menuitems:
        output += "</br>"
        output += item.name
        output += "</br>"
        output += item.price
        output += "</br>"
        output += item.description
        output += "</br>"
        output += "<a href='/restaurant/%s/%d/edit/'>Edit</a>"%(restaurant_id,item.id)
        output += "</br>"
        output += "<a href='/restaurant/%s/%d/delete/'>Delete</a>"%(restaurant_id,item.id)
        output += "</br>"
    output += "<a href='/restaurant/%s/new/'>Add new menu item</a>"%restaurant_id   

    return output

@app.route('/restaurant/<int:restaurant_id>/new/', methods=('GET','POST'))
def newMenuItem(restaurant_id):
    
    if request.method == 'POST':
        ctype,pdict = cgi.parse_header(
            request.headers.environ['CONTENT_TYPE']
        )
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(request.input_stream,pdict)
            mName = fields.get('menuName')
            mCourse = fields.get('course')
            mdes = fields.get('description')
            mprice = fields.get('price')
            addNewMenuItem(mName,mCourse,mdes,mprice,restaurant_id)
    
    return render_template('addNewMenuItem.html')

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',methods=('GET','POST'))
def editMenuItem(restaurant_id, menu_id):
    menuitem = getMenuItem(restaurant_id,menu_id)
    if request.method == 'POST':
        ctype,pdict = cgi.parse_header(
            request.headers.environ['CONTENT_TYPE']
        )
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(request.input_stream,pdict)
            mName = fields.get('menuName')
            mCourse = fields.get('course')
            mdes = fields.get('description')
            mprice = fields.get('price')
            changeMenuItem(menu_id,mName,mCourse,mdes,mprice)
    
    return render_template('editMenuItem.html',name=menuitem.name,course=menuitem.course,description=menuitem.description,price=menuitem.price)


@app.route("/restaurant/<int:restaurant_id>/<int:menu_id>/delete/",methods=('GET','POST'))
def deleteMenuItem(restaurant_id, menu_id):
    menuitem = getMenuItem(restaurant_id,menu_id)
    if request.method == 'POST':
        deleteMenuItemdb(menu_id)
        output = "<h2>You deleted this menu item succesfully!</h2>"
        return output
    return render_template('deleteMenuItem.html',name = menuitem.name )
if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1',port = 5000)