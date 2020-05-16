from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models
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
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_artist = db.Column(db.String(120))
    seeking_artist_description = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='venue', lazy='joined')

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.genres} {self.seeking_artist} {self.seeking_artist_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    seeking_venue = db.Column(db.String(120))
    seeking_venue_description = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='artist', lazy='joined')

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.genres} {self.phone} {self.seeking_venue} {self.seeking_venue_description}>'
        #dander-repr method useful debugging statements when we print these objects.

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Shows(db.Model):
    __tablename__='Shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Shows {self.id}, Artist {self.Artist_id}>'

#
# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
