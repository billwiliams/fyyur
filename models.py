#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

db = SQLAlchemy()

migrate = Migrate(app, db, compare_type=True)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue',
                            passive_deletes=True, lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist',
                            passive_deletes=True, lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id', ondelete='CASCADE'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime)
