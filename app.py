#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from itertools import count
import json
from unicodedata import name
from urllib import response
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
from sqlalchemy import ARRAY
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:nneka2000@localhost:5432/musical'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------  
@app.route('/venues')
def venues():
  venues = Venue.query.all()
  data = [] 
  addresses = Venue.query.distinct(Venue.city, Venue.state).all()
  for address in addresses:
     data.append({
        'city':address.city,
        'state': address.state,
        'venues': [{
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
        }
      for venue in venues if
        venue.city == address.city and venue.state == address.state]
      }) 
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}')).all()
  data =[]
  for venue in venues:
    count = 0
    for shows in venue.shows:
      if(shows.start_time > datetime.now()):
        count+=1
    data.append({
      'id':venue.id,
      'name': venue.name,
      'num_upcoming_shows': count
    })   
  response={
    "count": len(data),
    "data":data
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  venue.upcoming_shows = [show for show in venue.shows if show.start_time > datetime.now()]
  venue.past_shows = [show for show in venue.shows if show.start_time < datetime.now()]
  return render_template('pages/show_venue.html', venue= venue)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = VenueForm(request.form)
    venue = Venue(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    genres = form.genres.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data
  )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' deleted!')
  except:
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' could not deleted!')
  finally:
    db.session.close()    
  return redirect(url_for('venues'))
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  try:
    db.session.delete(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' deleted!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' could not deleted!')
  finally: 
    db.session.close()
    return render_template('artist/home.html')
#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike( f'%{search_term}%' )).all()
  data = []
  for artist in artists:
    count = 0
    for shows in artist.shows:
       if(shows.start_time > datetime.now()):
        count+=1
    data.append({
      'id':artist.id,
      'name': artist.name,
      'num_upcoming_shows': count
   })       
  response={
    "count": len(data),
    "data":data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  artist.upcoming_shows = [show for show in artist.shows if show.start_time > datetime.now()]
  artist.past_shows = [show for show in artist.shows if show.start_time < datetime.now()]
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get_or_404(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website 
  form.facebook_link.data = artist.facebook_link 
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  return render_template('forms/edit_artist.html', form=form, artist = artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:  
    form = ArtistForm(request.form)
    artist = Artist.query.get_or_404(artist_id)
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data 
    artist.phone = form.phone.data
    artist.website = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:  
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()     
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(request.form)
  venue.name = form.name.data
  venue.genres = form.genres.data
  venue.address = form.address.data
  venue.city = form.city.data
  venue.state = form.state.data 
  venue.phone = form.phone.data
  venue.website = form.website_link.data
  venue.facebook_link = form.facebook_link.data
  venue.image_link = form.image_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_description = form.seeking_description.data
  db.session.add(venue)
  db.session.commit() 
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
  form = ArtistForm(request.form)
  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occured! Artist ' + request.form['name'] + ' was not successfully listed!')
    db.session.rollback()
  finally:
    db.session.close()    
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by('start_time').all()
  data = []
  for show in shows:
      data.append(
      {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      }
      )
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = ShowForm(request.form)
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
     flash('An error occurred. Show could not be listed.')
     db.session.rollback()
  finally:
    db.session.commit()
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