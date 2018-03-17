# Laptop Service
from passlib.apps import custom_app_context as pwd_context
from flask import Flask, request, make_response, render_template, jsonify, url_for, redirect, session
from flask_restful import Resource, Api
from pymongo import MongoClient
from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)
from urllib.parse import urlparse, urljoin
from wtforms import Form, BooleanField, StringField, validators, PasswordField
from flask_login import LoginManager,  UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
api = Api(app)
app.config["SECRET_KEY"] = "test1234@#$"
app.config["LENGTH"] = 0
app.config["duration"] = 300
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

client = MongoClient("db", 27017)
db = client.tododb

class User(UserMixin):
    def __init__(self):
        self.token = None

@login_manager.user_loader
def user_loader(user_id, _token = None):
    data = db.tododb.find_one({"Location": int(user_id)})
    if data:
        user = User()
        user.id = user_id
        user.token = _token
        return user
    else:
        return


def is_safe_url(url):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, url))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


class RegisterForm(Form):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])


class LoginForm(Form):
    username = StringField("Username", validators=[validators.DataRequired()])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    remember_me = BooleanField("Remember Me")


def hash_password(password):
    return pwd_context.encrypt(password)

def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

def generate_auth_token(_id, expiration=600):
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    # pass index of user
    return s.dumps({'id': _id})

def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    return True

@app.route("/api/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    username = form.username.data
    password = form.password.data
    item = db.tododb.find_one({"username":username})
    if username is None or password is None:
        return render_template("register.html", form=form)
    elif item is not None:
        return "Bad Request: The username already exists", 400
    else:
        password = hash_password(str(password))
        app.config["LENGTH"] = app.config["LENGTH"] + 1
        _id = app.config["LENGTH"]
        item = {"username":username, "password": password, "Location": _id}
        db.tododb.insert_one(item)
        return redirect(url_for(login_manager.login_view))


@app.route("/api/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    _next = request.args.get("next")
    if is_safe_url(_next) is False:
        return "Bad Request", 400
    if form.validate() and request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        app.logger.debug(username)
        data = db.tododb.find_one({"username": username})
        app.logger.debug(data)
        if data is not None:
            hash_word = data["password"]
            if verify_password(password, hash_word):
                user = User()
                user.id = data["Location"]
                login_user(user, remember=True)
                return redirect(url_for("token"))
        else:
            return redirect(url_for("register"))
    return render_template("login.html", form=form)


@app.route("/api/token")
@login_required
def token():
    user_id = current_user.id
    _token = generate_auth_token(user_id, 300)
    session["token"] = _token
    return make_response(jsonify({"token": _token.decode('ascii'), "duration": app.config["duration"]}), 201)


@app.route("/api/logout")
@login_required
def logout():
    logout_user()
    return "Logout."


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for(login_manager.login_view))


class UserRequest(Resource):
    def get(self, _id):
        item = db.tododb.find_one({"Location": _id})
        if _id is None or item is None:
            return "Bad Request", 400
        else:
            return {"username": item["username"], "Location": item["Location"]}


def top_k():
    top = request.args.get("top")
    if top:
        item = db.tododb.find({"open": {"$exists": True}}).limit(int(top))
    else:
        item = db.tododb.find({"open": {"$exists": True}})
    return item


def find_and_append(item, item_list):
    dictionary = {}
    for key in item_list:
        dictionary[key] = []
    for i in item:
        for key in item_list:
            try:
                dictionary[key].append(i[key])
            except KeyError:
                return "Empty"
    return dictionary


def find_and_add(item,item_list):
    csv = ""
    for key in item_list:
        csv += key + " "
    csv += ": "
    for i in item:
        for key in item_list:
            try:
                csv += key + ": " + i[key] + " "
            except KeyError:
                return "Empty"
        csv += "|| "
    return csv

class Laptop(Resource):
    def get(self):
        return {
            'Laptops': ['Mac OS', 'Dell',
            'Windozzee',    'Yet another laptop!',
            'Yet yet another laptop!'
        ]
            }

class listAll(Resource):
    @login_required
    def get(self):
        _token = session.get("token")
        if _token is not None:
            if verify_auth_token(_token):
                key_list = ["open", "close"]
                data = top_k()
                _open_close = find_and_append(data, key_list)
                return _open_close
            else:
                return redirect(url_for(login_manager.login_view))
        else:
            return "Unauthorized: None token", 401


class listAllCsv(Resource):
    @login_required
    def get(self):
        _token = session.get("token")
        if _token is not None:
            if verify_auth_token(_token):
                key_list = ["open", "close"]
                data = top_k()
                all_csv = find_and_add(data, key_list)
                return all_csv
            else:
                return redirect(url_for(login_manager.login_view))
        else:
            return "Unauthorized: None token", 401


class listOpenOnly(Resource):
    @login_required
    def get(self):
        _token = session.get("token")
        if _token is not None:
            if verify_auth_token(_token):
                key_list = ["open"]
                data = top_k()
                _open = find_and_append(data, key_list)
                return _open
            else:
                return redirect(url_for(login_manager.login_view))
        else:
            return "Unauthorized: None token", 401


class listOpenOnlyCsv(Resource):
    @login_required
    def get(self):
        _token = session.get("token")
        if _token is not None:
            if verify_auth_token(_token):
                key_list = ["open"]
                data = top_k()
                open_csv = find_and_add(data, key_list)
                return open_csv
            else:
                return redirect(url_for(login_manager.login_view))
        else:
            return "Unauthorized: None token", 401


class listCloseOnly(Resource):
    @login_required
    def get(self):
        _token = session.get("token")
        if _token is not None:
            if verify_auth_token(_token):
                key_list = ["close"]
                data = top_k()
                _close = find_and_append(data, key_list)
                return _close
            else:
                return redirect(url_for(login_manager.login_view))
        else:
            return "Unauthorized: None token", 401


class listCloseOnlyCsv(Resource):
    @login_required
    def get(self):
        _token = session.get("token")
        if _token is not None:
            if verify_auth_token(_token):
                key_list = ["close"]
                data = top_k()
                close_csv = find_and_add(data, key_list)
                return close_csv
            else:
                return redirect(url_for(login_manager.login_view))
        else:
            return "Unauthorized: None token", 401




# Create routes
# Another way, without decorators
api.add_resource(Laptop, '/')
api.add_resource(UserRequest, "/api/users/<int:_id>")
api.add_resource(listAll, '/listAll', '/listAll/json')
api.add_resource(listOpenOnly, '/listOpenOnly', '/listOpenOnly/json')
api.add_resource(listCloseOnly, '/listCloseOnly', '/listCloseOnly/json')

api.add_resource(listAllCsv, '/listAll/csv')
api.add_resource(listOpenOnlyCsv, '/listOpenOnly/csv')
api.add_resource(listCloseOnlyCsv, '/listCloseOnly/csv')
# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
