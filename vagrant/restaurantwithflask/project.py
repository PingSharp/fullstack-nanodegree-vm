from flask import Flask
from flask import (render_template,request,url_for,redirect,flash,jsonify)
app = Flask(__name__)
import cgi
import os
from flask import session as login_session
import random,string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
from flask import make_response
import requests
from database_setup import Restaurant, Base, MenuItem, User

CLIENT_ID = json.loads(
    open('secret.json','r').read()
)['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"
 
engine = create_engine('sqlite:///restaurantmenuwithusers.db')
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
def DeleteRestaurant(rid):
    restaurants = session.query(Restaurant)
    deleteObj = restaurants.filter_by(id=rid).one()
    session.delete(deleteObj)
    session.commit()
def deleteMenuItemdb(mid):
    deleteItem = session.query(MenuItem).filter_by(id=mid).one()
    session.delete(deleteItem)
    session.commit()
def AddNewRestaurant(rname,uId):
    restaurant1 = Restaurant(name = rname,user_id = uId)
    session.add(restaurant1)
    session.commit()
def changeNameOfRestaurant(rid,rname):
    restaurants = session.query(Restaurant)
    restaurant = restaurants.filter_by(id=rid).first()
    restaurant.name = rname
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
def addNewUser(uname,uemail,upicture):
    newUser = User(name=uname,email=uemail,picture=upicture)
    session.add(newUser)
    session.commit()
def addNewMenuItem(rname,rcourse,rdes,rprice,rid,uId):
    newMenuItem = MenuItem(name=rname,course=rcourse,description=rdes,price=rprice,Restaurant_id=rid,user_id=uId)
    session.add(newMenuItem)
    session.commit()
def getMenuItem(rid,mid):
    menuitems = session.query(MenuItem).filter_by(Restaurant_id = rid)
    menuitem = menuitems.filter_by(id=mid)
    mi = menuitem.one()
    return mi
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
# protect user away for session hijacking,if user open the login page,he will get a random state code.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state']=state
    return render_template('login.html',STATE=state)

@app.route('/gconnect',methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('secret.json',scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'),401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'%access_token)
    print access_token
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dump("Token's user ID doesnt match given user ID"),401
        )
        response.header['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    login_session['access_token'] = credentials.access_token
    login_session['provider'] = 'google'
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        createUser(login_session)
        if checkUserHasRestaurant(login_session['user_id']):
            return redirect('/restaurants/')
        else:
            response = make_response('False',200)
            response.headers['Content-Type'] = 'text/plain'
            return response
        
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    params = {'access_token': credentials.access_token}
    answer = requests.get(userinfo_url,params=params)

    data = answer.json()
    user = session.query(User).filter_by(id=1).one();
    print user
    
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    createUser(login_session)
    if checkUserHasRestaurant(login_session['user_id']):
        return redirect('/restaurants/')
    else:
        response = make_response('False',200)
        response.headers['Content-Type'] = 'text/plain'
        return response
@app.route('/fconnect',methods=['POST'])
def fconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    ht = httplib2.Http()
    code = request.data
    app_id = json.loads(open('fbSecret.json','r').read())['web']['app_id']
    app_secret = json.loads(open('fbSecret.json','r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'%(app_id,app_secret,code)
    results = ht.request(url,'GET')[1]
    print results
    stringArray = results.split('"')
    print stringArray
    token = stringArray[3]
    userInfoUrl = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email'%token
    h = httplib2.Http()
    result = h.request(userInfoUrl,'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['accesstoken'] = token
    login_session['username'] = data['name']
    login_session['facebookid'] = data['id']
    login_session['email'] = data['email']
    createUser(login_session)
    if checkUserHasRestaurant(login_session['user_id']):
        return redirect('/restaurants/')
    else:
        response = make_response('False',200)
        response.headers['Content-Type'] = 'text/plain'
        return response
@app.route('/disconnect')
def disconnect():
    if login_session['provider'] == 'google':
        return redirect(url_for('gdisconnect'))
    elif login_session['provider'] == 'facebook':
        return redirect(url_for('fdisconnect'))

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print"access_token is none,the user is not connected"
        response = make_response(json.dump("current user not connected!"),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result1 = h.request(url,'GET')
    result2 = result1[0]
    print login_session
    print result1
    print result2
    if result2['status'] == '200':
        if 'provider' in login_session:
            del login_session['provider'] 
        if 'gplus_id' in login_session:
            del login_session['gplus_id']
        if 'access_token' in login_session:
            del login_session['access_token']
        if 'username' in login_session:
            del login_session['username']
        if 'email' in login_session:
            del login_session['email']
        if 'picture' in login_session:
            del login_session['picture']
        if 'user_id' in login_session:
            del login_session['user_id']
       
        response = make_response(json.dumps("succesfully disconnected!"),200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps("Failed to revoke token for given user.",400))
        response.headers["Content-Type"] = 'application/json'
        return response
@app.route('/fdisconnect')
def fdisconnect():
    facebookId = login_session.get('facebookid')
    accessToken = login_session.get('accesstoken')
    if accessToken is None:
        print"token is none,the user is not connected"
        response = make_response(json.dump("current user not connected!"),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print"user name is %s"%login_session['username']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (login_session['facebookid'],accessToken)
    h = httplib2.Http()
    result1 = h.request(url,'DELETE')[1]
   
    print result1
    if 'provider' in login_session:
        del login_session['provider'] 
    if 'accesstoken' in login_session:
        del login_session['accesstoken']
    if 'facebookid' in login_session:
        del login_session['facebookid']
    if 'username' in login_session:
        del login_session['username']
    if 'email' in login_session:
        del login_session['email']
    if 'user_id' in login_session:
        del login_session['user_id']
    if 'picture' in login_session:
        del login_session['picture']
    response = make_response(json.dumps("succesfully disconnected!"),200)
    response.headers['Content-Type'] = 'application/json'
    return response
   
def createUser(login_session):
    userExist = getUserId(login_session['email'])
    if(userExist == None):
        usertable = session.query(User)
        print usertable
        addNewUser(login_session['username'],login_session['email'],login_session['picture'])
        login_session['user_id'] = getUserId(login_session['email'])
    else:
        print "User exist!id:%s"%userExist
        login_session['user_id'] = userExist

def getUserInfo(userId):
    user = session.query(User).filter_by(id = userId).one()
    return user
def getUserId(userEmail):
    try:   
        user = session.query(User).filter_by(email=userEmail).one()
        userId = user.id
        return userId
    except:
        return None
def checkUserHasRestaurant(userId):
    try:
        restaurant = session.query(Restaurant).filter_by(user_id=userId).one().name
        return True
    except:
        return False
        

@app.route('/')
@app.route('/restaurants/')
def restaurants():
    if 'username' in login_session and 'user_id' in login_session:
        if checkUserHasRestaurant(login_session['user_id']):

            restaurants = getAllRestaurants()
            return render_template('restaurants.html',res = restaurants)
        else:
            return redirect(url_for('restaurantsforPublic'))
    else:
        return redirect(url_for('showLogin'))

@app.route('/')
@app.route('/restaurantsforpublic/')
def restaurantsforPublic():
    if 'username' in login_session and 'user_id' in login_session:
        if not checkUserHasRestaurant(login_session['user_id']):
            restaurants = getAllRestaurants()
            return render_template('restaurantspublic.html',res = restaurants)
        else:
            return redirect(url_for('restaurants'))
    else:
        return redirect(url_for('showLogin'))

@app.route('/restaurants/<int:restaurant_id>/edit/',methods=('GET','POST'))
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        res = getRestaurantById(restaurant_id)
        if request.method == 'POST':
            rName =request.form['restaurantName']
            changeNameOfRestaurant(restaurant_id,rName)
            flash("You have changed the name of the restaurant %s succesfully!"%rName)
            return redirect(url_for('restaurants'))
        return render_template('editRestaurant.html',name = res.name)

@app.route('/restaurants/<int:restaurant_id>/delete/',methods=('GET','POST'))
def deleteRestaurant(restaurant_id):
    if 'username'  not in login_session:
        return redirect(url_for('showLogin'))
    else:
        if request.method == 'POST':
            DeleteRestaurant(restaurant_id)
            flash("You have deleted the restaurant succesfully!")
            return redirect(url_for('restaurants'))
        return render_template('deleteRestaurant.html')

@app.route('/restaurants/new/',methods=('GET','POST'))
def addNewRestaurant():
    if 'username'  not in login_session:
        return redirect(url_for('showLogin'))
    else:
        if request.method == 'POST':
            rName = request.form['restaurantName']
            uId = getUserId(login_session['email'])
            AddNewRestaurant(rName)
            flash("You have added a new restaurant succesfully!")
            return redirect(url_for('restaurants'))
        return render_template('addNewRestaurant.html')

@app.route('/restaurants/JSON/')
def restaurantsJson():
    restaurants = getAllRestaurants()
    return jsonify(restautants = [res.serialize for res in restaurants])
@app.route('/restaurants/<int:restaurant_id>/JSON/')
def restaurantJson(restaurant_id):
    restaurant = getRestaurantById(restaurant_id)
    return jsonify(restaurant = restaurant.serialize)

@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    
    menuitems = session.query(MenuItem).filter_by(Restaurant_id = restaurant_id)  
    restaurant = getRestaurantById(restaurant_id)
    return render_template('menu.html',items = menuitems,rid = restaurant_id,res = restaurant )

@app.route('/restaurant/<int:restaurant_id>/new/', methods=('GET','POST'))
def newMenuItem(restaurant_id):
    if 'username'  not in login_session:
        return redirect(url_for('showLogin'))
    else:
        if request.method == 'POST':
            mName = request.form['menuName']
            mCourse = request.form['course']
            mdes = request.form['description']
            mprice = request.form['price']
            uid = getUserId(login_session['email'])
    #      ctype,pdict = cgi.parse_header(
    #         request.headers.environ['CONTENT_TYPE']
    #     )
    #     if ctype == 'multipart/form-data':
    #         fields = cgi.parse_multipart(request.input_stream,pdict)
    #         mName = fields.get('menuName')
    #         mCourse = fields.get('course')
    #         mdes = fields.get('description')
    #         mprice = fields.get('price')
            addNewMenuItem(mName,mCourse,mdes,mprice,restaurant_id,uid) 
            flash("You have added the menu item succesfully! ")
            return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
    
        return render_template('addNewMenuItem.html')

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',methods=('GET','POST'))
def editMenuItem(restaurant_id, menu_id):
    if 'username'  not in login_session:
        return redirect(url_for('showLogin'))
    else:
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
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
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
