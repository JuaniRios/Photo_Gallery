from flask_login import LoginManager
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

login = LoginManager()
db = SQLAlchemy()


class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PicturesModel(db.Model):
    __tablename__ = 'pictures'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel', backref=db.backref('pictures', lazy=True))
    country = db.Column(db.Text())
    town = db.Column(db.Text())
    date = db.Column(db.Text())
    data = db.Column(db.LargeBinary)


class FacesModel(db.Model):
    __tablename__ = 'faces'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User who uploaded source pic
    user = db.relationship('UserModel', backref=db.backref('faces', lazy=True))
    person_id = db.Column(db.Text())
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id'), nullable=False) # Source picture of the face
    picture = db.relationship('PicturesModel')
    data = db.Column(db.LargeBinary)


class NamesModel(db.Model):
    __tablename__ = 'names'
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Text(), db.ForeignKey('faces.person_id'))
    name = db.Column(db.Text(), default='Unknown')
    person = db.relationship('FacesModel')
    picture = db.Column(db.LargeBinary)

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
