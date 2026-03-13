from flask import Flask, redirect, request, url_for
from flask import Response

import requests

from flask import request
from flask import Flask, render_template

from jinja2 import Template
import secrets

import base64
import json
import os


from flask import session


app = Flask(__name__)

app.secret_key = secrets.token_hex() 


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, ForeignKey, String

from logging.config import dictConfig


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },
     'file.handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'weatherportal.log',
            'maxBytes': 10000000,
            'backupCount': 5,
            'level': 'DEBUG',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file.handler']
    }
})

# Not required for assignment3
in_mem_cities = []
in_mem_user_cities = {}


# SQLite Database creation
Base = declarative_base()
engine = create_engine("sqlite:///weatherportal.db", echo=True, future=True)
DBSession = sessionmaker(bind=engine)


@app.before_first_request
def create_tables():
    Base.metadata.create_all(engine)


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<Admin(name='%s')>" % (self.name)

    # Ref: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
        fields = {}
        for c in self.__table__.columns:
            fields[c.name] = getattr(self, c.name)
        return fields


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s')>" % (self.name)

    def as_dict(self):
        fields = {}
        for c in self.__table__.columns:
            fields[c.name] = getattr(self, c.name)
        return fields


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True, autoincrement=True)
    adminid = Column(Integer, ForeignKey('admin.id'))
    name = Column(String)
    url = Column(String)

    def __repr__(self):
        return "<City(name='%s')>" % (self.name)

    def as_dict(self):
        fields = {}
        for c in self.__table__.columns:
            fields[c.name] = getattr(self, c.name)
        return fields


class UserCity(Base):
    __tablename__ = 'usercity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('user.id'))
    cityId = Column(Integer, ForeignKey('city.id'))
    month = Column(String)
    year = Column(String)
    weather_params = Column(String)

    def __repr__(self):
        return "<UserCity(userId='%s', cityId='%s')>" % (self.userId, self.cityId)

    def as_dict(self):
        fields = {}
        for c in self.__table__.columns:
            fields[c.name] = getattr(self, c.name)
        return fields


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s')>" % (self.name)

    def as_dict(self):
        fields = {}
        for c in self.__table__.columns:
            fields[c.name] = getattr(self, c.name)
        return fields


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True, autoincrement=True)
    adminid = Column(Integer, ForeignKey('admin.id'))
    name = Column(String)
    url = Column(String)

    def __repr__(self):
        return "<City(name='%s')>" % (self.name)

    def as_dict(self):
        fields = {}
        for c in self.__table__.columns:
            fields[c.name] = getattr(self, c.name)
        return fields


class UserCity(Base):
    __tablename__ = 'usercity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('user.id'))
    cityId = Column(Integer, ForeignKey('city.id'))
    month = Column(String)
    year = Column(String)
    weather_params = Column(String)

    def __repr__(self):
        return "<UserCity(userId='%s', cityId='%s')>" % (self.userId, self.cityId)

    def as_dict(self):
        fields = {}
        for c in self.__table__.columns:
            fields[c.name] = getattr(self, c.name)
        return fields



## Admin REST API
@app.route("/admin", methods=['POST'])
def add_admin():
    app.logger.info("Inside add_admin")
    data = request.json
    app.logger.info("Received request:%s", str(data))

    name = data['name']
    password = data['password']

    admin = Admin(name=name, password=password)

    session = DBSession()
    session.add(admin)
    session.commit()

    return admin.as_dict()


@app.route("/admin")
def get_admins():
    app.logger.info("Inside get_admins")
    ret_obj = {}

    session = DBSession()
    admins = session.query(Admin)
    admin_list = []
    for admin in admins:
        admin_list.append(admin.as_dict())

    ret_obj['admins'] = admin_list
    return ret_obj


@app.route("/admin/<id>")
def get_admin_by_id(id):
    app.logger.info("Inside get_admin_by_id %s\n", id)

    session = DBSession()
    admin = session.get(Admin, id)

    app.logger.info("Found admin:%s\n", str(admin))
    if admin == None:
        status = ("Admin with id {id} not found\n").format(id=id)
        return Response(status, status=404)
    else:
        return admin.as_dict()


@app.route("/admin/<id>", methods=['DELETE'])
def delete_admin_by_id(id):
    app.logger.info("Inside delete_admin_by_id %s\n", id)

    session = DBSession()
    admin = session.query(Admin).filter_by(id=id).first()

    app.logger.info("Found admin:%s\n", str(admin))
    if admin == None:
        status = ("Admin with id {id} not found.\n").format(id=id)
        return Response(status, status=404)
    else:
        session.delete(admin)
        session.commit()
        status = ("Admin with id {id} deleted.\n").format(id=id)
        return Response(status, status=200)


@app.route("/logout",methods=['GET'])
def logout():
    app.logger.info("Logout called.")
    session.pop('username', None)
    app.logger.info("Before returning...")
    return render_template('index.html')


@app.route("/login", methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    app.logger.info("Username:%s", username)
    app.logger.info("Password:%s", password)

    session['username'] = username

    my_cities = []
    if username in in_mem_user_cities:
        my_cities = in_mem_user_cities[username]
    return render_template('welcome.html',
            welcome_message = "Personal Weather Portal",
            cities=my_cities,
            name=username,
            addButton_style="display:none;",
            addCityForm_style="display:none;",
            regButton_style="display:inline;",
            regForm_style="display:inline;",
            status_style="display:none;")


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/adminlogin", methods=['POST'])
def adminlogin():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    app.logger.info("Username:%s", username)
    app.logger.info("Password:%s", password)

    session['username'] = username

    user_cities = in_mem_cities
    return render_template('welcome.html',
            welcome_message = "Personal Weather Portal - Admin Panel",
            cities=user_cities,
            name=username,
            addButton_style="display:inline;",
            addCityForm_style="display:inline;",
            regButton_style="display:none;",
            regForm_style="display:none;",
            status_style="display:none;")


@app.route("/admin")
def adminindex():
    return render_template('adminindex.html')


## Section 2: User REST API

@app.route("/users", methods=['POST'])
def add_user():
    app.logger.info("Inside add_user")
    data = request.json
    app.logger.info("Received request:%s", str(data))

    name = data['name']
    password = data['password']

    db = DBSession()
    existing = db.query(User).filter_by(name=name).first()
    if existing:
        return Response("User with %s already exists." % name, status=400)

    user = User(name=name, password=password)
    db.add(user)
    db.commit()
    return user.as_dict()


@app.route("/users")
def get_users():
    app.logger.info("Inside get_users")
    db = DBSession()
    users = db.query(User).all()
    return {"users": [u.as_dict() for u in users]}


@app.route("/users/<id>")
def get_user_by_id(id):
    app.logger.info("Inside get_user_by_id %s", id)
    db = DBSession()
    user = db.get(User, id)
    if user is None:
        return Response("User with id %s not found." % id, status=404)
    return user.as_dict()


@app.route("/users/<id>", methods=['DELETE'])
def delete_user_by_id(id):
    app.logger.info("Inside delete_user_by_id %s", id)
    db = DBSession()
    user = db.query(User).filter_by(id=id).first()
    if user is None:
        return Response("User with id %s not found." % id, status=404)
    db.delete(user)
    db.commit()
    return Response("User with %s deleted." % id, status=200)


## Section 3: Admin Cities REST API

@app.route("/admin/<admin_id>/cities", methods=['POST'])
def add_city(admin_id):
    app.logger.info("Inside add_city for admin %s", admin_id)
    db = DBSession()
    admin = db.get(Admin, admin_id)
    if admin is None:
        return Response("Admin with id %s not found." % admin_id, status=404)

    data = request.json
    city = City(adminid=admin_id, name=data['name'], url=data['url'])
    db.add(city)
    db.commit()
    return city.as_dict()


@app.route("/admin/<admin_id>/cities")
def get_cities(admin_id):
    app.logger.info("Inside get_cities for admin %s", admin_id)
    db = DBSession()
    admin = db.get(Admin, admin_id)
    if admin is None:
        return Response("Admin with id %s not found." % admin_id, status=404)

    cities = db.query(City).filter_by(adminid=admin_id).all()
    return {"cities": [c.as_dict() for c in cities]}


@app.route("/admin/<admin_id>/cities/<city_id>")
def get_city_by_id(admin_id, city_id):
    app.logger.info("Inside get_city_by_id admin:%s city:%s", admin_id, city_id)
    db = DBSession()
    admin = db.get(Admin, admin_id)
    if admin is None:
        return Response("Admin with id %s not found." % admin_id, status=404)

    city = db.get(City, city_id)
    if city is None:
        return Response("City with id %s not found." % city_id, status=404)
    return city.as_dict()


@app.route("/admin/<admin_id>/cities/<city_id>", methods=['DELETE'])
def delete_city_by_id(admin_id, city_id):
    app.logger.info("Inside delete_city_by_id admin:%s city:%s", admin_id, city_id)
    db = DBSession()
    admin = db.get(Admin, admin_id)
    if admin is None:
        return Response("Admin with id %s not found." % admin_id, status=404)

    city = db.query(City).filter_by(id=city_id).first()
    if city is None:
        return Response("City with id %s not found." % city_id, status=404)
    db.delete(city)
    db.commit()
    return Response("City with %s deleted." % city_id, status=200)


## Section 4: User-City Tracking REST API

@app.route("/users/<user_id>/cities", methods=['POST'])
def add_user_city(user_id):
    app.logger.info("Inside add_user_city for user %s", user_id)
    db = DBSession()

    user = db.get(User, user_id)
    if user is None:
        return Response("User with id %s not found." % user_id, status=404)

    data = request.json
    city_name = data['name']
    year = data.get('year', '')

    if not str(year).isdigit() or len(str(year)) != 4:
        return Response("Year needs to be exactly four digits.", status=400)

    city = db.query(City).filter_by(name=city_name).first()
    if city is None:
        return Response("City with name %s not found." % city_name, status=404)

    user_city = UserCity(
        userId=user_id,
        cityId=city.id,
        month=data['month'],
        year=str(year),
        weather_params=data.get('weather_params', data.get('params', ''))
    )
    db.add(user_city)
    db.commit()
    return user_city.as_dict()


@app.route("/users/<user_id>/cities")
def get_user_cities(user_id):
    app.logger.info("Inside get_user_cities for user %s", user_id)
    db = DBSession()

    user = db.get(User, user_id)
    if user is None:
        return Response("User with id %s not found." % user_id, status=404)

    # 4.3: filter by city name if ?name= query param provided
    city_name = request.args.get('name')
    if city_name:
        city = db.query(City).filter_by(name=city_name).first()
        if city is None:
            return Response("City with name %s not found." % city_name, status=404)

        uc = db.query(UserCity).filter_by(userId=user_id, cityId=city.id).first()
        if uc is None:
            return Response(
                "City with name %s not being tracked by the user %s." % (city_name, user.name),
                status=404
            )
        return {
            "name": city.name,
            "month": uc.month,
            "year": uc.year,
            "weather_params": uc.weather_params
        }

    # 4.2: return all user cities
    user_cities = db.query(UserCity).filter_by(userId=user_id).all()
    return {"usercities": [uc.as_dict() for uc in user_cities]}


if __name__ == "__main__":

    app.debug = False
    app.logger.info('Portal started...')
    app.run(host='0.0.0.0', port=5009)