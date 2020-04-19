#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from flask_migrate import Migrate
import logging
import sys
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import exc
#import dictfier
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:AmmaNaana1!@@localhost:5432/fyyur'
db = SQLAlchemy(app)
migrate = Migrate(app,db) # to include migrate functionality

#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# TODO: connect to a local postgresql database -- given sql info in config.py - done


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
    phone = db.Column(db.String(120),default='')

    image_link = db.Column(db.String(500),default='')
    facebook_link = db.Column(db.String(120), default='')
    genres = db.Column(JSON)
    website = db.Column(db.String(500),default='')
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))
    ven_shows = db.relationship('Show',backref='ven_shows',lazy=True,cascade="all, delete-orphan") #to delete all shows if a venue is deleted 

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - done

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(JSON)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))
    art_shows = db.relationship('Show',backref='art_shows',lazy=True,cascade="all, delete-orphan") #to delete all shows if an artist is deleted 

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - done

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration - done

class Show(db.Model):
  __tablename__='Show'
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  start_time = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en')

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
  # DONE - TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  # first step - lets get list of venues ordered by stae and city
  venueslist = db.session.query(Venue).order_by('city','state').all()
  data=[]
  
  #Initialize two variables cityPrev and staePrev , to keep track of when a new city and stae data starts coming
  cityPrev = None
  statePrev = None

  #venuesbycityareadict  -> dict for each city and state
  venuesbycityareadict={}

  #venues -> list of venues that belong to each city and state.
  venues=[]

  # iterate through above list
  #populate the venuesbycityareadict only once - that is when we get new city and new state than the previouus value
  #keep adding each venues details to venuesbycityareadict 
  # Finally add venuesbycityareadict to venues list which gets set as a paramater of venuesbycityareadict
  # At the end of each cycle of for loop, add the venuesbycityareadict to a list and pass it to GUI via render template
  for venue in venueslist:
   # print("first line",venue.city,venue.state)
    ven={}
    ven['id'] = venue.id
    ven['name'] = venue.name
    shows = venue.ven_shows
    print(' shooowss ',shows)
    ven['num_upcoming_shows'] = 0 # len([v for v in venue.ven_shows if venue.ven_shows.start_time > datetime.now()])
    for show in shows:
      if(show.start_time > datetime.now()):
        ven['num_upcoming_shows'] = ven['num_upcoming_shows']+1

   
    if not cityPrev == venue.city or not statePrev == venue.state:
      venuesbycityareadict={}
      venues=[]
      venuesbycityareadict['city'] = venue.city
      venuesbycityareadict['state'] = venue.state
      venuesbycityareadict['venues'] = venues
    
    venues.append(ven)
   
    if not venuesbycityareadict in data:
      data.append(venuesbycityareadict)

    cityPrev = venue.city
    statePrev = venue.state
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE - TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" -done
  
  #search term
  search_term=request.form.get('search_term', '')
  # Query to get the list
  respList = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  #Initialize the main response as empty dict
  response = {}
  response['count'] = len(respList)
  data = []
  response['data']=data
  # iterate and populate the required data
  for resp in respList:
    dat = {}
    dat['id'] = resp.id
    dat['name'] = resp.name
    dat['num_upcoming_shows'] = 0
    for show in resp.ven_shows:
      if(show.start_time > datetime.now()):
        ven['num_upcoming_shows'] = ven['num_upcoming_shows']+1
    data.append(dat)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE - TODO: replace with real venue data from the venues table, using venue_id - done

  #data list - final list we send to GUI
  dataList = []
  #First get the venue list
  #Lopp through venue list and populate data accordingly 
  # For shows and artists, first get shows for each venue and then get artist information for each show based on the artist_id column in show tabe 
  #Populate artist data and show count based on the show start time into upcoming shows list or past shows list
  # For Artists where there is no image lin, we dont want a shoddy image link to be shown with no actual image, so make corresponding css change for image in main.css 
  #to now show anything when image source is empty
  venueList = Venue.query.all()
  for venue in venueList:
    ven={}
    for property, value in vars(venue).items():
      if property != '_sa_instance_state':
        ven[property]=value
    
    ven['past_shows']=[]
    ven['upcoming_shows']=[]
    past_shows_count=0
    upcoming_shows_count=0
    shows = venue.ven_shows
    for show in venue.ven_shows:
      artistbyid = Artist.query.get(show.artist_id)
      artist={}
      artist['start_time']=str(show.start_time)
      artist['artist_id']=artistbyid.id
      artist['artist_name']=artistbyid.name
      artist['artist_image_link']=artistbyid.image_link
      if(show.start_time > datetime.now()):
        past_shows_count = past_shows_count+1
        ven['upcoming_shows'].append(artist)
      else:
        upcoming_shows_count = upcoming_shows_count+1
        ven['past_shows'].append(artist)
    ven['upcoming_shows_count'] = upcoming_shows_count
    ven['past_shows_count'] = past_shows_count
    dataList.append(ven)
  
  data = list(filter(lambda d: d['id'] == venue_id, dataList))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # DONE - TODO: insert form data as a new Venue record in the db, instead
  # DONE - TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  error=False
  seeking_talent=False
  seeking_description=''
  image_link=''
  website=''
  if form.validate():
    print('form validated')
    try:
      if 'seeking_talent' in request.form:
        seeking_talent = request.form['seeking_talent'] == 'y'
      if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']
      if 'website' in request.form:
        website = request.form['website']
      if 'image_link' in request.form:
        image_link = request.form['image_link']
      new_venue = Venue(
        name=request.form['name'],
        genres=request.form.getlist('genres'),
        address=request.form['address'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        website=website,
        facebook_link=request.form['facebook_link'],
        image_link=image_link,
        seeking_talent=seeking_talent,
        seeking_description=seeking_description,
            )
      db.session.add(new_venue)
      db.session.commit()
    except exc.SQLAlchemyError as e:
      print("its unfortinately error scenario :(", e)
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
      db.session.close()
      print('in finally')
  else:
    error=True
    print("form validation failed",form.errors)
      
  if not error:
      #return body
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
      print("error")
      flash('An error occurred. Venue ' + request.form['name']  + ' could not be listed.')
      #abort(400)
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # DONE - TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE - TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    print(" Succesfully deleted venue with id ", venue_id)
  except exc.SQLAlchemyError as e:
    db.session.rollback()
    print(sys.exc_info())
    print(" Error - Cound not deleted venue with id ", venue_id)
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE - TODO: replace with real data returned from querying the database
  artistList = Artist.query.all()
  data=[]
  for artist in artistList:
    art={}
    art['id'] = artist.id
    art['name'] = artist.name
    data.append(art)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  #search term
  search_term=request.form.get('search_term', '')
  # Query to get the list
  respList = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  #Initialize the main response as empty dict
  response = {}
  response['count'] = len(respList)
  data = []
  response['data']=data
  # iterate and populate the required data
  for resp in respList:
    dat = {}
    dat['id'] = resp.id
    dat['name'] = resp.name
    data.append(dat)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE- TODO: replace with real venue data from the venues table, using venue_id
  artistList = Artist.query.all()
  dataList=[]
  for artist in artistList:
    art={}
    for property, value in vars(artist).items():
      if property != '_sa_instance_state':
        art[property]=value
    art['past_shows']=[]
    art['upcoming_shows']=[]
    past_shows_count=0
    upcoming_shows_count=0
    shows = artist.art_shows
    for show in shows:
      venuebyid = Venue.query.get(show.venue_id)
      venue={}
      venue['start_time']= str(show.start_time)
      venue['venue_id']=venuebyid.id
      venue['venue_name']=venuebyid.name
      venue['venue_image_link']=venuebyid.image_link
      if(show.start_time > datetime.now()):
        past_shows_count = past_shows_count+1
        art['upcoming_shows'].append(venue)
      else:
        upcoming_shows_count = upcoming_shows_count+1
        art['past_shows'].append(venue)
    art['upcoming_shows_count'] = upcoming_shows_count
    art['past_shows_count'] = past_shows_count
    dataList.append(art)
 
  
  data = list(filter(lambda d: d['id'] == artist_id, dataList))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  #Just get the artist object from primary key, here, venue id
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE - TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  error=False
  form = ArtistForm(request.form)
  if form.validate():
    print('form validated')
    try:

      artist.name=request.form['name'],
      artist.genres=request.form.getlist('genres'),
      artist.city=request.form['city'],
      artist.state=request.form['state'],
      artist.phone=request.form['phone'],
      artist.facebook_link=request.form['facebook_link']
          
      db.session.commit()
    except exc.SQLAlchemyError as e:
      print("its unfortinately error scenario :(", e)
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
      db.session.close()
      print('in finally')
  else:
    error=True
    print("form validation failed",form.errors)
      
  if not error:
      #return body
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
  else:
      print("error")
      flash('An error occurred. Artist ' + request.form['name']  + ' could not be updated.')


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  #Just get the form object from primary key, here, venue id
  venue = Venue.query.get(venue_id)
  # DONE- TODO: populate form with values from venue with ID <venue_id> - sone
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE- TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  error=False
  form = VenueForm(request.form)

  if form.validate():
    print('form validated')
    try:

      venue.name=request.form['name'],
      venue.genres=request.form.getlist('genres'),
      venue.address=request.form['address'],
      venue.city=request.form['city'],
      venue.state=request.form['state'],
      venue.phone=request.form['phone'],
      venue.facebook_link=request.form['facebook_link']
          
      db.session.commit()
    except exc.SQLAlchemyError as e:
      print("its unfortinately error scenario :(", e)
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
      db.session.close()
      print('in finally')
  else:
    error=True
    print("form validation failed",form.errors)
      
  if not error:
      #return body
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  else:
      print("error")
      flash('An error occurred. Venue ' + request.form['name']  + ' could not be updated.')

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
  # DONE TODO: insert form data as a new Venue record in the db, instead
  #  DONE TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  error=False
  seeking_venue=False
  seeking_description=''
  image_link=''
  website=''
  if form.validate():
    print('form validated')
    try:
      if 'seeking_venue' in request.form:
        seeking_venue = request.form['seeking_venue'] == 'y'
      if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']
      if 'website' in request.form:
        website = request.form['website']
      if 'image_link' in request.form:
        image_link = request.form['image_link']
      new_artist = Artist(
        name=request.form['name'],
        genres=request.form.getlist('genres'),
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        website=website,
        facebook_link=request.form['facebook_link'],
        image_link=image_link,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description
            )
      db.session.add(new_artist)
      db.session.commit()
    except exc.SQLAlchemyError as e:
      print("its unfortinately error scenario :(", e)
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
      db.session.close()
      print('in finally')
  else:
    error=True
    print("form validation failed",form.errors)
  
  if not error:
      #return body
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
      print("error")
      flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
      #abort(400)

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE- TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  showList = Show.query.all()
  dataList=[]
  for shows in showList:
    showData={}
    showData['venue_id'] = shows.venue_id
    showData['artist_id'] = shows.artist_id
    showData['start_time'] = str(shows.start_time)
    showData['venue_name']=Venue.query.get(shows.venue_id).name
    artist=Artist.query.get(shows.artist_id)
    showData['artist_name']= artist.name
    showData['artist_image_link']=artist.image_link
    dataList.append(showData)

  return render_template('pages/shows.html', shows=dataList)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE- TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  error=False
  if form.validate():
    print('form validated')
    try:
      
      new_show = Show(
        artist_id=request.form['artist_id'],
        venue_id=request.form.get('venue_id'),
        start_time=request.form['start_time']
        
            )
      db.session.add(new_show)
      db.session.commit()
    except exc.SQLAlchemyError as e:
      print("its unfortinately error scenario :(", e)
      db.session.rollback()
      error=True
      print(sys.exc_info())
    finally:
      db.session.close()
      print('in finally')
  else:
    error=True
    print(" show form validation failed",form.errors)
      
  if not error:
      #return body
      flash('Show was successfully listed!')

  else:
      print("error")
      flash('Show was not successfully listed!')
      #abort(400)

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
