from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
#from flask.ext.seasurf import SeaSurf
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from catalog_setup import Base, Catagory, Object, User
from flask import session as login_session
import random
import string
import datetime
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
#csrf = SeaSurf(app)

@app.route('/hello')
def hello():
   return 'Hello, world!'


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog client 1"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response





# Return the catagory Id given the catagory name
def getCatagoryId(catagory_name):
    catagory = session.query(Catagory).filter_by(name = catagory_name).one()
    return catagory.id

# Return the catagory name given the catagory id
def getCatagoryName(catagory_id):
    catagory = session.query(Catagory).filter_by(id = catagory_id).one()
    return catagory.name

# Return the object Id given the object name
def getObjectId(object_name):
    object = session.query(Object).filter_by(name = object_name).one()
    return object.object_id

# Return the object name given the object id
def getObjectName(object_id):
    object = session.query(Object).filter_by(id = object_id).one()
    return object.name

# JSON APIs to view Catagory Information
@app.route('/catalog/<string:catagory_name>/items/JSON')
def catagoryObjectJSON(catagory_name):
    catagory_id = getCatagoryId(catagory_name)
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    objects = session.query(Object).filter_by(
        catagory_id=catagory_id).all()
    return jsonify(Objects=[i.serialize for i in objects])


@app.route('/catalog/<string:catagory_name>/<string:object_name>/JSON')
def objectJSON(catagory_name, object_name):
    object_id = getObjectId(object_name)
    object = session.query(Object).filter_by(object_id=object_id).one()
    return jsonify(Object=object.serialize)


@app.route('/catalog/JSON')
def catagoriesJSON():
    catagories = session.query(Catagory).all()
    return jsonify(catagories=[r.serialize for r in catagories])


# Show all catagories
@app.route('/')
@app.route('/catalog/')
def showCatagories():
    catagories = session.query(Catagory).order_by(asc(Catagory.name))
    objects = session.query(Object).order_by(asc(Object.name)).all()
    object_category_mapping = []
    for item_object in objects:
        x = item_object, getCatagoryName(item_object.catagory_id)
        object_category_mapping.append(x)

    if 'username' not in login_session:
        return render_template('publiccatagories.html', catagories=catagories, objects=object_category_mapping)
    else:
        return render_template('catagories.html', catagories=catagories, objects=object_category_mapping)

# Create a new catagory
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatagory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCatagory = Catagory(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCatagory)
        flash('New Catagory %s Successfully Created' % newCatagory.name)
        session.commit()
        return redirect(url_for('showCatagories'))
    else:
        return render_template('newCatagory.html')

# Create a new item for a catagory
def newObject(catagory_name):
    catagory_id = getCatagoryId(catagory_name)
    if 'username' not in login_session:
        return redirect('/login')
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    if login_session['user_id'] != catagory.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add object objects to this catagory. Please create your own catagory in order to add objects.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newObject = Object(name=request.form['name'], description=request.form['description'], catagory_id=catagory_id, user_id=catagory.user_id)
        session.add(newObject)
        session.commit()
        flash('New Object %s Object Successfully Created' % (newObject.name))
        return redirect(url_for('showObject', catagory_name=catagory_name))
    else:
        return render_template('newObject.html', catagory_name=catagory_name)

# Edit a catagory
'''
@app.route('/catalog/<string:catagory_name>/edit/', methods=['GET', 'POST'])
def editCatagory(catagory_name):
    catagory_id = getCatagoryId(catagory_name)
    editedCatagory = session.query(
        Catagory).filter_by(id=catagory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCatagory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this catagory. Please create your own catagory in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCatagory.name = request.form['name']
            flash('Catagory Successfully Edited %s' % editedCatagory.name)
            return redirect(url_for('showCatagories'))
    else:
        return render_template('editCatagory.html', catagory=editedCatagory)
'''

# Delete a catagory
@app.route('/catalog/<string:catagory_name>/delete/', methods=['GET', 'POST'])
def deleteCatagory(catagory_name):
    catagory_id = getCatagoryId(catagory_name)
    objectsToDelete = session.query(Object).filter_by(catagory_id=catagory_id).all()
    catagoryToDelete = session.query(
        Catagory).filter_by(id=catagory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catagoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this catagory. Please create your own catagory in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        for objects in objectsToDelete:
            session.delete(objects)
        session.delete(catagoryToDelete)
        flash('%s Successfully Deleted' % catagoryToDelete.name)
        session.commit()
        return redirect(url_for('showCatagories', catagory_id=catagory_id))
    else:
        return render_template('deleteCatagory.html', catagory=catagoryToDelete)

# Show a catagory's object
@app.route('/catalog/<string:catagory_name>/')
@app.route('/catalog/<string:catagory_name>/items/')
def showObject(catagory_name):
    catagory_id = getCatagoryId(catagory_name)
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()    
    creator = getUserInfo(catagory.user_id)
    objects = session.query(Object).filter_by(catagory_id=catagory_id).all()
    if 'username' not in login_session:
        return render_template('publicObject.html', objects=objects, catagory=catagory, creator=creator)
    else:
        return render_template('object.html', objects=objects, catagory=catagory, creator=creator)

# Displays the description of the item
@app.route('/catalog/<string:catagory_name>/<string:object_name>/')
def showDescription(catagory_name, object_name):
    catagory_id = getCatagoryId(catagory_name)
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    creator = getUserInfo(catagory.user_id)
    objects = session.query(Object).filter_by(catagory_id=catagory_id).all()
    object = session.query(Object).filter_by(name = object_name).one()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicDescription.html', object=object, catagory=catagory, creator=creator)
    else:
        return render_template('publicDescription.html', object=object, catagory=catagory, creator=creator)

# Redirects the URL to the description page from the front page
@app.route('/catalog/<string:catagory_id>/<string:object_name>/description')
def showDescriptionRedirect(catagory_id, object_name):
    catagory_name = getCatagoryName(catagory_id)
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    creator = getUserInfo(catagory.user_id)
    objects = session.query(Object).filter_by(catagory_id=catagory_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return redirect(url_for('showDescription', object_name=object_name, catagory_name=catagory_name))
    else:
        return redirect(url_for('showDescription', object_name=object_name, catagory_name=catagory_name))

# Create a new object object
@app.route('/catalog/<string:catagory_name>/object/new/', methods=['GET', 'POST'])
def newObject(catagory_name):
    catagory_id = getCatagoryId(catagory_name)
    if 'username' not in login_session:
        return redirect('/login')
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    if login_session['user_id'] != catagory.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add object objects to this catagory. Please create your own catagory in order to add objects.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newObject = Object(name=request.form['name'], description=request.form['description'], catagory_id=catagory_id, user_id=catagory.user_id)
        session.add(newObject)
        session.commit()
        flash('New Object %s Object Successfully Created' % (newObject.name))
        return redirect(url_for('showObject', catagory_name=catagory_name))
    else:
        return render_template('newObject.html', catagory_name=catagory_name)

# Edit a object object
@app.route('/catalog/<string:catagory_name>/object/<string:object_name>/edit', methods=['GET', 'POST'])
def editObject(catagory_name, object_name):
    catagory_id = getCatagoryId(catagory_name)
    object_id = getObjectId(object_name)
    if 'username' not in login_session:
        return redirect('/login')
    editedObject = session.query(Object).filter_by(object_id=object_id).one()
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    if login_session['user_id'] != catagory.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit object objects to this catagory. Please create your own catagory in order to edit objects.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedObject.name = request.form['name']
        if request.form['description']:
            editedObject.description = request.form['description']
        session.add(editedObject)
        session.commit()
        flash('Object Object Successfully Edited')
        return redirect(url_for('showObject', catagory_name=catagory_name))
    else:
        return render_template('editObject.html', catagory_id=catagory_id, object_id=object_id, object=editedObject)


# Delete a object object
@app.route('/catalog/<string:catagory_name>/object/<string:object_name>/delete', methods=['GET', 'POST'])
def deleteObject(catagory_name, object_name):
    catagory_id = getCatagoryId(catagory_name)
    object_id = getObjectId(object_name)
    if 'username' not in login_session:
        return redirect('/login')
    catagory = session.query(Catagory).filter_by(id=catagory_id).one()
    objectToDelete = session.query(Object).filter_by(object_id=object_id).one()
    if login_session['user_id'] != catagory.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete object objects to this catagory. Please create your own catagory in order to delete objects.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(objectToDelete)
        session.commit()
        flash('Object Object Successfully Deleted')
        return redirect(url_for('showObject', catagory_name=catagory_name))
    else:
        return render_template('deleteObject.html', object=objectToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatagories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatagories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5040)