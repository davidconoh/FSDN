#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
# from utils import  filter_shows_past, filter_shows_upcoming
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    genres = db.Column(db.String(120), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True)
   
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def venue_page_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'genres': json.loads(self.genres),
            'all_shows': [Show.artist_details(Show.query.get(show.id)) for show in self.shows]
        }

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def artist_page_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'genres': json.loads(self.genres),
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'all_shows': [Show.venue_details(Show.query.get(show.id)) for show in self.shows]
        }

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time}>'
    
    def artist_details(self):
        artist = Artist.query.get(self.artist_id)
        return {
            'artist_id': self.artist_id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
    
    def venue_details(self):
        venue = Venue.query.get(self.venue_id)
        return {
            'venue_id': self.venue_id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  city_state_for_venue = ''
  error = False
  try:
    venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    for venue in venues:
      if venue.city + venue.state == city_state_for_venue:
        data[len(data) - 1]['venues'].append({
          "id": venue.id,
          "name": venue.name,
        })
      else:
        city_state_for_venue = venue.city + venue.state
        data.append({
          "city": venue.city,
          "state": venue.state,
          "venues": [{
            "id": venue.id,
            "name": venue.name,
          }]
        })
  except:
    error = True
    flash('An error occured getting list of venues')
    print(sys.exc_info())
  finally:
    if error:
      return redirect(url_for('index'))
    else:
      return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  response = {}
  try:
    search_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    data = [
        {
          "id": search.id,
          "name": search.name,
        } for search in search_results]
    response = {
      "count": len(data),
      "data": data
    }
  except:
    response = {}
    print(sys.exc_info())
  finally:
    db.session.close()
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error = False
  data = {}
  try:
    error = False
    query = Venue.query.get(venue_id)
    data = Venue.venue_page_details(query)
    if data['all_shows'] is not []:
      data['past_shows'] = list(filter(filter_shows_past, data['all_shows']))
      data['past_shows_count'] = len(data['past_shows'])
      data['upcoming_shows'] = list(filter(filter_shows_upcoming, data['all_shows']))
      data['upcoming_shows_count'] = len(data['upcoming_shows'])
  except:
    error = True
    flash(message='An error occured getting venue details', category='warning')
    print(sys.exc_info())
  finally:
    if error:
      return redirect(url_for('index'))
    else:
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
  venue_form = VenueForm(request.form)
  try:
    venue = Venue(
      name=venue_form.name.data,
      city=venue_form.city.data,
      state=venue_form.state.data,
      address=venue_form.address.data,
      phone=venue_form.phone.data,
      image_link=venue_form.image_link.data,
      facebook_link=venue_form.facebook_link.data,
      website_link=venue_form.website_link.data,
      seeking_talent=venue_form.seeking_talent.data,
      seeking_description=venue_form.seeking_description.data,
      genres=json.dumps(venue_form.genres.data)
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('You have successfully deleted the venue')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured trying to delete the venue')
  finally:
    db.session.close()
    return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  response = {}
  try:
    search_results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
    data = [
        {
          "id": search.id,
          "name": search.name,
        } for search in search_results]
    response = {
      "count": len(data),
      "data": data
    }
  except:
    response = {}
    print(sys.exc_info())
  finally:
    db.session.close()
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  error = False
  data = {}
  try:
    error = False
    query = Artist.query.get(artist_id)
    data = Artist.artist_page_details(query)
    if data['all_shows'] is not []:
      data['past_shows'] = list(filter(filter_shows_past, data['all_shows']))
      data['past_shows_count'] = len(data['past_shows'])
      data['upcoming_shows'] = list(filter(filter_shows_upcoming, data['all_shows']))
      data['upcoming_shows_count'] = len(data['upcoming_shows'])
  except:
    error = True
    flash(message='An error occured getting artist details', category='warning')
    print(sys.exc_info())
  finally:
    if error:
      return redirect(url_for('index'))
    else:
      return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  error = False
  try:
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
  except:
    error = True
    flash('An error occured getting Artist details!')
    print(sys.exc_info())
  finally:
    if error:
      return redirect(url_for('index'))
    else:
      # TODO: populate form with fields from artist with ID <artist_id>
      return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_form = ArtistForm(request.form)
  try:
    artist = Artist.query.get(artist_id)
    artist.name=artist_form.name.data
    artist.city=artist_form.city.data
    artist.state=artist_form.state.data
    artist.phone=artist_form.phone.data
    artist.image_link=artist_form.image_link.data
    artist.facebook_link=artist_form.facebook_link.data
    artist.website_link=artist_form.website_link.data
    artist.seeking_venue=artist_form.seeking_venue.data
    artist.seeking_description=artist_form.seeking_description.data
    artist.genres=json.dumps(artist_form.genres.data)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    print(sys.exc_info())
  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  error = False
  try:
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
  except:
    error = True 
    flash('An error occured getting Venue details!')
    print(sys.exc_info())
  # TODO: populate form with values from venue with ID <venue_id>
  finally:
    if error:
      return redirect(url_for('index'))
    else:
      return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue_form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    venue.name=venue_form.name.data
    venue.city=venue_form.city.data
    venue.state=venue_form.state.data
    venue.address=venue_form.address.data
    venue.phone=venue_form.phone.data
    venue.image_link=venue_form.image_link.data
    venue.facebook_link=venue_form.facebook_link.data
    venue.website_link=venue_form.website_link.data
    venue.seeking_talent=venue_form.seeking_talent.data
    venue.seeking_description=venue_form.seeking_description.data
    venue.genres=json.dumps(venue_form.genres.data)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    print(sys.exc_info())
  finally:
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
  artist_form = ArtistForm(request.form)
  try:
    artist = Artist(
      name=artist_form.name.data,
      city=artist_form.city.data,
      state=artist_form.state.data,
      phone=artist_form.phone.data,
      image_link=artist_form.image_link.data,
      genres=json.dumps(artist_form.genres.data),
      facebook_link=artist_form.facebook_link.data,
      website_link=artist_form.website_link.data,
      seeking_venue=artist_form.seeking_venue.data,
      seeking_description=artist_form.seeking_description.data,
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
    return render_template('pages/home.html')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  error = False
  try:
    shows = db.session.query(Show).join(Artist).join(Venue).all()
    for show in shows: 
      data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name, 
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S') 
      })
    error = False 
  except:
    error = True
    flash(message='An error occured getting show details', category='warning')
    print(sys.exc_info())
  finally:
    if error:
      return redirect(url_for('index'))
    else:
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
  show_form = ShowForm(request.form)
  try:
    show = Show(
      venue_id=show_form.venue_id.data,
      artist_id=show_form.artist_id.data,
      start_time=show_form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
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