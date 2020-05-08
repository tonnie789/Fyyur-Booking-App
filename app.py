#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime, timedelta

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database (completed)

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
    start_time = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Shows {self.id}, Artist {self.Artist_id}>'

#
# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


 # Venues
 # ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.order_by(Venue.id, Venue.state, Venue.city).all()
  states_cities = ''
  now = datetime.now()
  data = []

  for venue in venues:
    upcomingShows = db.session.query(Venue).join(Shows, Shows.venue_id == Venue.id).filter(Shows.start_time>now).all()
    if states_cities == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": len(upcomingShows)
      })
    else:
      states_cities == venue.city + venue.state
      data.append({
        "city":venue.city,
        "state":venue.state,
        "venues": [{
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(upcomingShows)
        }]
      })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')
  venue_list = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).all()
  result = []

  for r in venue_list:
      result.append({
        "id": r.id,
        "name": r.name,
      })

      response={
        "count":len(venue_list),
        "data": result
      }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # venues = Venue.query.filter_by(id=venue_id).first()
  venues = db.session.query(Venue).filter(Venue.id == venue_id).first()
  shows = Shows.query.filter_by(venue_id=venue_id).all()
  past = datetime.utcnow() - timedelta(days=1)
  present = datetime.now()
  upcoming_shows_count = db.session.query(Venue).join(Shows, Shows.venue_id == venue_id).filter(Shows.venue_id == venue_id, Shows.start_time > past).count()
  past_shows_count = db.session.query(Venue).join(Shows, Shows.venue_id == venue_id).filter(Shows.venue_id == venue_id, Shows.start_time < past).count()
  past_shows = []
  upcoming_shows = []

  for s in shows:
      print(s.start_time <= present)
      if s.start_time <= present:
          past_shows.append({
          "arist_id":s.artist.id,
          "artist_name":s.artist.name,
          "artist_image_link":s.artist.image_link,
          "start_time": s.start_time.strftime('%d/%m/%y %H:%M:%S')
          })
      elif s.start_time >= present:
          upcoming_shows.append({
          "arist_id":s.artist.id,
          "artist_name":s.artist.name,
          "artist_image_link":s.artist.image_link,
          "start_time": s.start_time.strftime('%d/%m/%y %H:%M:%S')
          })

  data = {
     "id": venues.id,
     "name": venues.name,
     "genres": venues.genres,
     "address": venues.address,
     "city": venues.city,
     "state": venues.state,
     "phone": venues.phone,
     "facebook_link": venues.facebook_link,
     "seeking_talent": venues.seeking_artist,
     "seeking_description": venues.seeking_artist_description,
     "image_link": venues.image_link,
     "past_shows": past_shows,
     "past_shows_count": len(past_shows),
     "upcoming_shows": (upcoming_shows),
     "upcoming_shows_count": len(upcoming_shows),
     }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    venue = Venue (
       name = request.form ['name'],
       city = request.form ['city'],
       state = request.form ['state'],
       address = request.form ['address'],
       phone = request.form ['phone'],
       genres = request.form.getlist('genres'),
       facebook_link = request.form ['facebook_link'],
       seeking_artist = request.form['seeking_artist'],
       seeking_artist_description = request.form ['seeking_artist_description'],
       image_link = request.form ['image_link'],
       )
    try:
       db.session.add(venue)
       db.session.commit()
  # on successful db insert, flash success
       flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('Venue was successfully deleted!')
  except:
      flash('Venue was unsuccessfully deleted!')
  finally:
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by(Artist.id, Artist.name).all()#orders the artist information accordingly
  data = []

  for a in artists:
      data.append({
        "id":a.id,
        "name":a.name
        })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term')
  artist_list = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all()
  result = []

  for r in artist_list:
      result.append({
        "id":r.id,
        "name":r.name,
        })

      response={
        "count":len(artist_list),
        "data":result
        }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  shows = Shows.query.filter_by(artist_id=artist_id).all()
  past = datetime.utcnow() - timedelta(days=1)
  present = datetime.utcnow()
  upcoming_shows_count = db.session.query(Artist).join(Shows, Shows.artist_id == artist_id).filter(Shows.artist_id == artist_id, Shows.start_time > past).count()
  past_shows_count = db.session.query(Artist).join(Shows, Shows.artist_id == artist_id).filter(Shows.artist_id == artist_id, Shows.start_time < past).count()
  past_shows = []
  upcoming_shows = []

  for s in shows:
      print(s.artist.image_link)
      if s.start_time <= past:
          past_shows.append({
          "arist_id":s.artist.id,
          "artist_name":s.artist.name,
          "artist_image_link":s.artist.image_link,
          "start_time": s.start_time.strftime('%d/%m/%y %H:%M:%S')
          })
      elif s.start_time >= present:
          upcoming_shows.append({
          "arist_id":s.artist.id,
          "artist_name":s.artist.name,
          "artist_image_link":s.artist.image_link,
          "start_time": s.start_time.strftime('%d/%m/%y %H:%M:%S')
          })

  data = {
     "id": artist.id,
     "name": artist.name,
     "genres": artist.genres,
     "city": artist.city,
     "state": artist.state,
     "phone": artist.phone,
     "facebook_link": artist.facebook_link,
     "seeking_venue": artist.seeking_venue,
     "seeking_venue_description": artist.seeking_venue_description,
     "image_link": artist.image_link,
     "past_shows": past_shows,
     "past_shows_count": len(past_shows),
     "upcoming_shows": upcoming_shows,
     "upcoming_shows_count": len(upcoming_shows),
     }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_data = db.session.query(Artist).filter(Artist.id == artist_id).one()

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    artist_data = db.session.query(Artist).filter(Artist.id == artist_id).one()

    if artist_data:
        form = ArtistForm (formdata=request.form, obj = artist_data)
        if request.method == 'POST' and form.validate():
            #save edits
            # save_changes(artist_data, form)
            db.session.commit()
            flash('Artist was successfully updated!')
        else:
           flash('Error, artist was unsuccessfully updated!')
           db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = db.session.query(Venue).filter(Venue.id == venue_id).one()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue_data = db.session.query(Venue).filter(Venue.id == venue_id).one()

  if venue_data:
      form = VenueForm (formdata=request.form, obj = venue_data)
      if request.method == 'POST' and form.validate():
          #save edits
          save_changes(venue_data, form)
          db.session.commit()
          flash('Artist was successfully updated!')
      else:
         flash('Error, venue was unsuccessfully updated!')
         db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
      artist = Artist (
         name = request.form ['name'],
         city = request.form ['city'],
         state = request.form ['state'],
         phone = request.form ['phone'],
         genres = request.form.getlist('genres'),
         image_link = request.form ['image_link'],
         facebook_link = request.form ['facebook_link'],
         seeking_venue = request.form['seeking_venue'],
         seeking_venue_description = request.form ['seeking_venue_description'],
         )
      try:
          db.session.add(artist)
          db.session.commit()
  # on successful db insert, flash success
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except:
          flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      finally:
        db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
      return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Shows.query.order_by(db.desc(Shows.start_time))
    data = []

    for s in shows:
        data.append({
        "venue_id":s.id,
        "venue_name":s.venue.name,
        "artist_id":s.artist.id,
        "artist_name":s.artist.name,
        "artist_image_link":s.artist.image_link,
        "start_time":s.start_time.strftime('%d/%m/%y %H:%M:%S')
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    show = Shows (
       artist_id = request.form ['artist_id'],
       venue_id = request.form ['venue_id'],
       start_time = request.form ['start_time'],
       )
    try:
       db.session.add(show)
       db.session.commit()
    # on successful db insert, flash success
       flash('Show was successfully listed!')
    except:
       flash('Error. Show was unsuccessfully listed!')
    finally:
       db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
