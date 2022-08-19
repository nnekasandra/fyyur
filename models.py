#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from flask_migrate import Migrate
from sqlalchemy import ARRAY
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
     _tablename_ = 'venue'
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String)
     city = db.Column(db.String(120))
     state = db.Column(db.String(120))
     address = db.Column(db.String(120))
     phone = db.Column(db.String(120))
     genres = db.Column(db.ARRAY(db.String(120)))
     image_link = db.Column(db.String(500))
     facebook_link = db.Column(db.String(120))
     website = db.Column(db.String(120))
     seeking_talent = db.Column(db.Boolean, default=False)
     seeking_description = db.Column(db.String(500))
     shows = db.relationship('Show', backref='venue', lazy='joined', cascade='delete')

class Artist(db.Model):
     _tablename_ = 'artist'
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String)
     city = db.Column(db.String(120))
     state = db.Column(db.String(120))
     phone = db.Column(db.String(120))
     genres = db.Column(db.ARRAY(db.String(120)))
     image_link = db.Column(db.String(500))
     facebook_link = db.Column(db.String(120))
     website = db.Column(db.String(120))
     seeking_venue = db.Column(db.Boolean, default=False)
     seeking_description = db.Column(db.String(500))
     shows = db.relationship('Show', backref='artist',lazy='joined', cascade='delete')

class Show(db.Model):
     _tablename_ = 'show' 
     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     artist_id = db.Column(db.ForeignKey('artist.id'), primary_key=True)
     venue_id = db.Column(db.ForeignKey('venue.id'), primary_key=True)
     start_time = db.Column(db.DateTime, nullable=False)
