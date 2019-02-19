from flask import Flask
from flask import (render_template,request,url_for,redirect,flash,jsonify)
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
    restaurants = session.query(Restaurant)
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
    item.name = nName
    item.course = nCourse
    item.description = nDes
    item.price = nPrice
    session.commit()

def getMenuItems(rid):
    menuitems = session.query(MenuItem).filter_by(Restaurant_id = rid)
    return menuitems
def addNewMenuItem(rname,rcourse,rdes,rprice,rid):
    newMenuItem = MenuItem(name=rname,course=rcourse,description=rdes,price=rprice,Restaurant_id=rid)
    session.add(newMenuItem)
    session.commit()
def getMenuItem(rid,mid):
    menuitems = session.query(MenuItem).filter_by(Restaurant_id = rid)
    menuitem = menuitems.filter_by(id=mid)
    mi = menuitem.one()
    return mi

@app.route('/')
@app.route('/restaurants/')
def restaurants():
    return render_template('restaurants.html')

@app.route('/restaurants/<int:restaurant_id>/edit/',methods=('GET','POST'))
def editRestaurant(restaurant_id):
    return render_template('editRestaurant.html')

@app.route('/restaurants/<int:restaurant_id>/delete/',methods=('GET','POST'))
def deleteRestaurant(restaurant_id):
    return render_template('deleteRestaurant.html')

@app.route('/restaurants/new/',methods=('GET','POST'))
def addNewRestaurant():
    return render_template('addNewRestaurant.html')

@app.route('/restaurants/JSON/')
def restaurantsJson():
    return"restaurants list in JSON"

@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantJson():
    return"restaurant in JSON"

@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    
    menuitems = session.query(MenuItem).filter_by(Restaurant_id = restaurant_id)  
    restaurant = getRestaurantById(restaurant_id)
    return render_template('menu.html',items = menuitems,rid = restaurant_id,res = restaurant )

@app.route('/restaurant/<int:restaurant_id>/new/', methods=('GET','POST'))
def newMenuItem(restaurant_id):
    
    if request.method == 'POST':
        mName = request.form['menuName']
        mCourse = request.form['course']
        mdes = request.form['description']
        mprice = request.form['price']
    #      ctype,pdict = cgi.parse_header(
    #         request.headers.environ['CONTENT_TYPE']
    #     )
    #     if ctype == 'multipart/form-data':
    #         fields = cgi.parse_multipart(request.input_stream,pdict)
    #         mName = fields.get('menuName')
    #         mCourse = fields.get('course')
    #         mdes = fields.get('description')
    #         mprice = fields.get('price')
        addNewMenuItem(mName,mCourse,mdes,mprice,restaurant_id) 
        flash("You have added the menu item succesfully! ")
        return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
    
    return render_template('addNewMenuItem.html')

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',methods=('GET','POST'))
def editMenuItem(restaurant_id, menu_id):
    menuitem = getMenuItem(restaurant_id,menu_id)
    if request.method == 'POST':
        mName = request.form['menuName']
        mCourse = request.form['course']
        mdes = request.form['description']
        mprice = request.form['price']
        # ctype,pdict = cgi.parse_header(
        #     request.headers.environ['CONTENT_TYPE']
        # )
        # if ctype == 'multipart/form-data':
        #     fields = cgi.parse_multipart(request.input_stream,pdict)
        #     mName = fields.get('menuName')
        #     mCourse = fields.get('course')
        #     mdes = fields.get('description')
        #     mprice = fields.get('price')
        changeMenuItem(menu_id,mName,mCourse,mdes,mprice)
        flash("You have changed the menu item succesfully!")
        return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
    
    return render_template('editMenuItem.html',name=menuitem.name,course=menuitem.course,description=menuitem.description,price=menuitem.price)


@app.route("/restaurant/<int:restaurant_id>/<int:menu_id>/delete/",methods=('GET','POST'))
def deleteMenuItem(restaurant_id, menu_id):
    menuitem = getMenuItem(restaurant_id,menu_id)
    if request.method == 'POST':
        deleteMenuItemdb(menu_id)
        output = "<h2>You deleted this menu item succesfully!</h2>"
        output += "<a href='/restaurant/%s/'>return</a>"%restaurant_id
        return output
    return render_template('deleteMenuItem.html',name = menuitem.name )

@app.route("/restaurant/<int:restaurant_id>/menu/JSON")
def getMenuItemsJson(restaurant_id):
    items = getMenuItems(restaurant_id)
    return jsonify(menuItems = [ i.serialize for i in items])
@app.route("/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON")
def getMenuItemJson(restaurant_id,menu_id):
    item = getMenuItem(restaurant_id,menu_id)
    return jsonify(menuItem = item.serialize)
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run(host='127.0.0.1',port = 9000)