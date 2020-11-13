#=======================================
# imports                              |
#=======================================

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from hashlib import sha256


#=======================================
# config                               |
#=======================================

current_path = os.path.dirname(os.path.realpath(__file__))

#__CAUTION__NO__SQLITE__IN__PRODUCTION__
#db_path = "sqlite:///test.db"
db_path = "postgresql://adminer:adminer@db:5432/adminer"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#=======================================
# databases                            |
#=======================================

class User(db.Model):
    """
    this is user orm class
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(256), unique=True)
    hash_password = db.Column(db.String(1024))
    role = db.Column(db.String(256))

    def __init__(user_login, raw_pass, user_role="user", user_coordinates, path_id):
        """Init of user class"""
        self.login = user_login
        self.hash_password = sha256(raw_pass).hexdigest()
        self.role = user_role
        self.coordinates = user_coordinates

    paths = db.relationship("Path", secondary=users_paths_association, back_populate="users")



# it this table we create
# many to many relationships 
# between user and his path's 
# including his readyness to go or not
# and coordinates
users_paths_association = db.Table(
    "users_paths", db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("paths_id", db.Integer, db.ForeignKey("paths.id")),
    db.Column("ready", db.Bool, nullable=False),
    db.Column("coordinate", db.String(128), nullable=False)
)

class Path(db.Model):
    """
    this is paths orm class
    """
    __tablename__ = "paths"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    
    def __init__(path_date):
        """Init of path class"""
        date = path_date

    users = db.relationship("User", secondary=users_paths_association, back_populate='paths')

#=======================================
# user api routes                      |
#=======================================

@app.route("/user/", methods=["GET"])
def list_users():
    """
    It should take nothing
    And return json array of all user's and their information
    """
    pass

@app.route("/user/", methods=["POST"])
def create_user():
    """
    It should be used for user creation
    so it takes all data from user model described earlier except id and relationships
    And return user's temporary jwt token ?
    """
    pass

@app.route("/user/", methods=["PUT"])
def update_user():
    """
    It should take user token and update database section
    And return well.... nothing
    """
    pass

@app.route("/user/", methods=["DELETE"])
def delete_user():
    """
    It should take user token and password
    And return nothing. just delete this user from database
    """
    pass

#=======================================
# path api routes                      |
#=======================================

@app.route("/path/", methods=["GET"])
def list_paths():
    """
    It should take limiter (for example 10 random path's)
    And return array of paths with all data provided except coordinates
    """
    pass

@app.route("/path/", methods=["POST"])
def create_path():
    """
    It should take all data needed for creation of path
    And no return
    """
    pass

@app.route("/path/", methods=["PUT"])
def update_path():
    """
    It should update all user information 
    and we need to check user token
    """
    pass

@app.route("/path/", methods=["DELETE"])
def delete_path():
    """
    it should take user token (it should be user with role admin or so) and password
    and no return. but delete this path from database
    """
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
    pass

@app.route("/users_paths/", methods=["GET"]):
def return_array_of_user_paths():
    """
    here we should take user token and return all his paths
    """
    pass

@app.route("/delete_user_path/", methods=["GET"])
def delete_user_path_assoc():
    """
    here we should take user token and delete his path
    """
    pass

#=======================================
# useful functions                     |
#=======================================

def raw_password_to_string():
    """
    actually that's just pass hashing lol
    """
    pass

#=======================================
# if main loop in development build    |
#=======================================
if __name__ == "__main__":
    app.run(debug=True)

