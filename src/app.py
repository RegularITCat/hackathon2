#=======================================
# imports                              |
#=======================================

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import hashlib
from os import path
import json
import datetime
from tsp import calc_path

#=======================================
# CONSTANT VALUES                      |
#=======================================

REQ_ERROR = "Error"
CONTENT_TYPE_ERROR = "Only Content-Type: application/json allowed"
DATABASE_INTEGRITY_ERROR = "Database integrity error"
TOKEN_ERROR = "Bad Token"
OK_STATUS = "Ok"
USER_NON_AUTHORISED = "Non-authorised"

#=======================================
# config                               |
#=======================================

current_path = path.dirname(path.realpath(__file__))

#__CAUTION__NO__SQLITE__IN__PRODUCTION__
#db_path = "sqlite:///test.db"
db_path = "postgresql://adminer:adminer@db:5432/adminer"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrete = Migrate(app, db)

#=======================================
# databases                            |
#=======================================

# it this table we create
# many to many relationships 
# between user and his path's 
# including his readyness to go or not
# and coordinates
#users_paths_association = db.Table(
#    "users_paths", db.metadata,
#    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
#    db.Column("path_id", db.Integer, db.ForeignKey("paths.id")),
#    db.Column("ready", db.Boolean, nullable=False),
#    db.Column("coordinate", db.String(128), nullable=False),
#    db.Column("first_name", db.String(128), nullable=False),
#    db.Column("second_name", db.String(128), nullable=False),
#    db.Column("phone", db.Integer, nullable=False)
#
#)


class UserPathAssociation(db.Model):
    """"""
    __tablename__ = "users_paths"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    path_id = db.Column(db.Integer, db.ForeignKey("paths.id"), nullable=False)
    ready = db.Column(db.Boolean, nullable=False)
    coordinate = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(128))
    second_name = db.Column(db.String(128))
    phone = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", backref="paths")
    path = db.relationship("Path", backref="users")


class User(db.Model):
    """
    this is user orm class
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(512), unique=True, nullable=False)
    hash_password = db.Column(db.String(4096), nullable=False)
    role = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(512))
    first_name = db.Column(db.String(256))
    second_name = db.Column(db.String(256))
    phone = db.Column(db.Integer)
    token = db.relationship("Token", uselist=False, back_populates="user")


class Path(db.Model):
    """
    this is paths orm class
    """
    __tablename__ = "paths"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime())
    start_coordinate = db.Column(db.String(256), nullable=False)
    end_coordinate = db.Column(db.String(256), nullable=False)


class Token(db.Model):
    """
    this is token orm class
    """
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(2048), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="token")

#=======================================
# user api routes                      |
#=======================================

@app.route("/user/", methods=["GET"])
def list_users():
    """
    It should take nothing
    And return json array of all user's and their information
    """
    if not check_content_type():
        return jsonify(status=CONTENT_TYPE_ERROR)
    reqdata = request.json
    if not check_token(reqdata["token"]):
        return jsonify(status=TOKEN_ERROR)
    users = db.session.query(User).all()
    resdata = []
    for user in users:
        resdata.append({"id" : user.id, "login" : user.login, "password" : user.hash_password})
    return jsonify(data=resdata, status=OK_STATUS)

@app.route("/user/sign_up", methods=["POST"])
def create_user():
    """
    It should be used for user creation
    so it takes all data from user model described earlier except id and relationships
    And return user's temporary jwt token ?
    """
    if not check_content_type():
        return jsonify(status=CONTENT_TYPE_ERROR)

    data = request.json
    #TODO check if request body contain required keys
    #if ["login", "password", "user", "email", "first_name", "second_name", "phone"].sort() != (data.keys()).sort():
    #    return jsonify(status="err")

    login = data["login"]
    hash_password = raw_password_to_string(str(data["password"]))
    role = "user"
    email = data["email"]
    first_name = data["first_name"]
    second_name = data["second_name"]
    phone = data["phone"] 
    #TODO data validation
    #if login == "" or hash_password == "" or role == "" or email == "" or first_name == "" or second_name == "":
    #    return jsonify(status="error")

    db.session.add(User(login=login, hash_password=hash_password, role=role, email=email, first_name=first_name, second_name=second_name, phone=phone))
    try:
        db.session.commit()
        return jsonify(status=OK_STATUS)
    except:
        db.session.rollback()
        return jsonify(status=DATABASE_INTEGRITY_ERROR)

@app.route("/user/", methods=["PUT"])
def update_user():
    """
    It should take user token and update database section
    And return well.... nothing
    """
    #TODO user update 
    pass

@app.route("/user/", methods=["DELETE"])
def delete_user():
    """
    It should take user token and password
    And return nothing. just delete this user from database
    """
    #TODO user delete
    pass

@app.route("/user/signin", methods=["POST"])
def sign_in():
    if not check_content_type():
        return jsonify(status=CONTENT_TYPE_ERROR)
    data = request.json
    login = data["login"]
    hash_password = raw_password_to_string(str(data["password"]))
    user = db.session.query(User).filter(db.and_(User.login==login, User.hash_password==hash_password)).first()
    if user != None:
        token=generate_token(login, hash_password)
        db.session.add(Token(token=token, date=datetime.datetime.today(), user_id=user.id))
        try:
            db.session.commit()
            return jsonify(token=token, status=OK_STATUS)
        except:
            db.session.rollback()
            return jsonify(status=DATABASE_INTEGRITY_ERROR)
    else:
        return jsonify(status=USER_NON_AUTHORISED)
        

#=======================================
# path api routes                      |
#=======================================

@app.route("/path/", methods=["GET"])
def list_paths():
    """
    It should take limiter (for example 10 random path's)
    And return array of paths with all data provided except coordinates (but when dev build it's okay)
    """
    paths = db.session.query(Path).all()
    data = []
    for path in paths:
        data.append({"id" : path.id,
            "title":path.title,"rating":path.rating,
            "description":path.description,"date":path.date,
            "start_coordinate":path.start_coordinate,
            "end_coordinate":path.end_coordinate})
    return jsonify(data=data, status=OK_STATUS)

@app.route("/path/", methods=["POST"])
def create_path():
    """
    It should take all data needed for creation of path
    And no return
    """
    if not check_content_type():
        return jsonify(status=CONTENT_TYPE_ERROR)
    data = request.json
    if not check_token(data["token"]):
        return jsonify(status=TOKEN_ERROR)
    #TODO check that we have required keys in request body to Path creation
    title = data["title"]
    rating = data["rating"]
    description = data["description"]
    date = datetime.datetime.fromisoformat(data["date"])
    start_coordinate = data["start_coordinate"]
    end_coordinate = data["end_coordinate"]
    #TODO data validation
    db.session.add(Path(title=title, rating=rating, description=description, date=date, start_coordinate=start_coordinate, end_coordinate=end_coordinate))
    try:
        db.session.commit()
        return jsonify(status=OK_STATUS)
    except:
        db.session.rollback()
        return jsonify(status=DATABASE_INTEGRITY_ERROR)

@app.route("/path/", methods=["PUT"])
def update_path():
    """
    It should update all user information 
    and we need to check user token
    """
    #TODO update path information
    pass

@app.route("/path/", methods=["DELETE"])
def delete_path():
    """
    it should take user token (it should be user with role admin or so) and password
    and no return. but delete this path from database
    """
    #TODO delete path from database
    pass

#=======================================
# other api routes                     |
#=======================================

@app.route("/user_path/", methods=["POST"])
def create_user_path_assoc():
    """
    we should take user token and path id
    and create assoc betweeb user and his password
    """
    if not check_content_type():
        return jsonify(status=CONTENT_TYPE_ERROR)
    reqdata = request.json
    if not check_token(reqdata["token"]):
        return jsonify(status=TOKEN_ERROR)
    #TODO check that request body contain needed data
    #if ["user_id", "path_id", "ready", "coordinate", "first_name", "second_name", "phone"].sort() != (data.keys()).sort():
    #    return jsonify(status="err")
    user_id = reqdata["user_id"]
    path_id = reqdata["path_id"]
    ready = True
    coordinate = reqdata["coordinate"]
    first_name = reqdata["first_name"]
    second_name = reqdata["second_name"]
    phone = reqdata["phone"]
    #TODO data validation
    user = db.session.query(User).filter(User.id==user_id).scalar() is not None
    path = db.session.query(Path).filter(Path.id==path_id).scalar() is not None
    if user and path:
        db.session.add(UserPathAssociation(user_id=user_id, path_id=path_id, ready=ready,coordinate=coordinate, first_name=first_name, second_name=second_name,phone=phone))
        try:
            db.session.commit()
            return jsonify(status=OK_STATUS)
        except:
            db.session.rollback()
            return jsonify(status=DATABASE_INTEGRITY_ERROR)
    else:
        return jsonify(status="err")

@app.route("/users_paths/", methods=["GET"])
def return_array_of_user_paths():
    """
    here we should take user token and return all his paths
    """
    if not check_content_type():
        return jsonify(status=CONTENT_TYPE_ERROR)
    reqdata = request.json
    if not check_token(reqdata["token"]):
        return jsonify(status=TOKEN_ERROR)
    user = db.session.query(User).get_or_404(reqdata["id"])
    print(user.paths[0].path.title)
    resdata = []
    for user_path in user.paths:
        resdata.append({"path id": user_path.path_id, "path title" : user_path.path.title})
    return jsonify(data=resdata, status=OK_STATUS)

@app.route("/delete_user_path/", methods=["DELETE"])
def delete_user_path_assoc():
    """
    here we should take user token and delete his path
    """
    #TODO delete user path assoc
    pass

#only for development purpose! CAUTION
@app.route("/token_list/", methods=["GET"])
def token_list():
    """
    return users token 
    """
    tokens = db.session.query(Token).all()
    resdata = []
    for token in tokens:
        resdata.append({"id" : token.id, "token":token.token, "user_id":token.user_id})
    return jsonify(data=resdata, status=OK_STATUS)

@app.route("/assoc_list/", methods=["GET"])
def assoc_list():
    """
    return all users registered at excursion
    """
    if not check_content_type():
        return jsonify(status=CONTENT_TYPE_ERROR)
    reqdata = request.json
    if not check_token(reqdata["token"]):
        return jsonify(status=TOKEN_ERROR)
    users_paths = db.session.query(UserPathAssociation).all()
    resdata = []
    for e in users_paths:
        resdata.append({"id" : e.id, "user_id":e.user_id, "path_id":e.path_id})
    return jsonify(data=resdata, status=OK_STATUS)

#dev test route
@app.route("/", methods=["GET"])
def test_route():
    """
    development demo for frontend work check
    """
    coordinates = "54.971288,82.875554|54.988211,82.906425|55.038288,82.937137|55.060150,82.984610"
    return jsonify(data=coordinates, status=OK_STATUS)

@app.route("/generate_coordinate/", methods=["GET"])
def generate_coordinate():
    """
    takes path_id and returns all waypoints
    """
    #TODO debug dat fucking code
    if not check_content_type():
        return jsonify(status=CONTENT_TYPE_ERROR)
    reqdata = request.json
    try:
        if not check_token(reqdata["token"]):
            return jsonify(status=TOKEN_ERROR)
    except:
        return jsonify(status=REQ_ERROR)
    path_id = reqdata["path_id"]
    path = db.session.query(Path).get_or_404(path_id)
    coordinate_data = []
    coordinate_data.append(path.start_coordinate)
    users_paths = path.users
    for e in users_paths:
        coordinate_data.append(e.coordinate)
            
    return jsonify(data=coordinate_data, status=OK_STATUS)

    #coordinate = (path.start_coordinate).split(",")
    #coordinate = (float(coordinate[0]), float(coordinate[1]))
    #coordinate_data.append(coordinate)
    #for user_path in path.users:
    #    coordinate = (user_path.coordinate).split(",")
    #    coordinate_data.append((float(coordinate[0]), float(coordinate[1])))
    #coordinate = (path.start_coordinate).split(",")
    #coordinate = (float(coordinate[0]), float(coordinate[1]))
    #try:
    #    final_coordinates = calc_path(coordinate, coordinate_data)
    #    final_str = ""
    #    for coordinate in final_coordinates:
    #        x, y = coordinate
    #        final_str += str(x) + "," + str(y) + "|"
    #    final_str = final_str[:-1]
    #    return jsonify(data=final_str, status=OK_STATUS)
    #except Exception as err:
    #    print(err)
    #    return jsonify(status=REQ_ERROR)

#=======================================
# useful functions                     |
#=======================================

def raw_password_to_string(raw_string):
    """
    actually that's just pass hashing lol
    """
    return hashlib.sha256(str(raw_string).encode('utf-8')).hexdigest()

def generate_token(login, password):
    """
    magic generation! very top secret
    """
    time = datetime.datetime.now().timestamp()
    raw_string = str(login) + str(password) + str(time)
    return hashlib.sha256(str(raw_string).encode('utf-8')).hexdigest()

def check_token(token):
    """
    return true in case if token valid
    """
    token = db.session.query(Token).filter(Token.token==token).first()
    if token == None:
        return False
    #TODO token lifetime
    #if (datetime.datetime.now() - token.date >= datetime.timedelta(day=2)):
    #    return False 
    return True

def check_content_type():
    """
    return true in case if http content-type header application/json
    """
    return request.content_type == "application/json"

#=======================================
# if code loop in development build    |
#=======================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

