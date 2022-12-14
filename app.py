#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.headerregistry import Address
from email.policy import default
import json
import dateutil.parser
import babel
from flask import (Flask,
                   render_template,
                   request,
                   Response,
                   flash,
                   redirect,
                   url_for)
from flask_moment import Moment

import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from models import app, db, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')
db.init_app(app)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    # allow even datetime objects to be passed
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    # date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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

    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    venue_locations = db.session.query(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    for venue_location in venue_locations:
        venue_state_city = {"city": venue_location.city,
                            "state": venue_location.state}
        # query for venue extra details
        venue_state_city['venues'] = []
        venues_in_state_city = db.session.query(Venue.id, Venue.name).\
            filter(Venue.state == venue_location.state,
                   Venue.city == venue_location.city).all()
        for venue in venues_in_state_city:
            # get number of upcoming shows
            num_upcoming_shows = Show.query.filter(Show.venue_id == venue.id).filter(
                Show.start_time >= datetime.today().date()).count()
            # append the venue details to the venue_details dict
            venue_details = {'id': venue.id, "name": venue.name,
                             "num_upcoming_shows": num_upcoming_shows}

            venue_state_city['venues'].append(venue_details)
        # append the combined state city with venues to the data list
        data.append(venue_state_city)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    response = {}

    search_term = request.form['search_term']

    # to enable search all names that have the search_term
    search_term = '%'+search_term+'%'

    # search query
    venues = db.session.query(Venue.id, Venue.name).filter(
        Venue.name.ilike(search_term))

    # No of venues
    venues_count = venues.count()

    response = {"count": venues_count}

    response["data"] = []
    # append venues in response
    for venue in venues.all():
        # aggregate number of supcoming shows per venue
        num_upcoming_shows = Show.query.filter(Show.venue_id == venue.id).\
            filter(Show.start_time >= datetime.today().date()).count()

        venue_details = {'id': venue.id, "name": venue.name,
                         "num_upcoming_shows": num_upcoming_shows}

        response["data"].append(venue_details)

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    venue = Venue.query.get(venue_id)

    # Venue details
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link
    }
    # Past Shows
    data["past_shows"] = []
    # past shows query
    past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id).\
        filter(Show.start_time < datetime.today().date())

    for past_show in past_shows.all():
        past_show_details = {"artist_id": past_show.Artist.id,
                             "artist_name": past_show.Artist.name,
                             "artist_image_link": past_show.Artist.image_link,
                             "start_time": past_show.start_time}
        data["past_shows"].append(past_show_details)

    data["past_shows_count"] = past_shows.count()

    # Upcoming Shows

    data["upcoming_shows"] = []
    upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id).\
        filter(Show.start_time >= datetime.today().date())

    for upcoming_show in upcoming_shows.all():
        upcoming_shows_details = {"artist_id": upcoming_show.Artist.id,
                                  "artist_name": upcoming_show.Artist.name,
                                  "artist_image_link": upcoming_show.Artist.image_link,
                                  "start_time": upcoming_show.start_time}
        data["upcoming_shows"].append(upcoming_shows_details)

    data["upcoming_shows_count"] = upcoming_shows.count()

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # obtain form
    form = VenueForm(request.form)
    if form.validate():
        try:
            # validate data

            venue = Venue(name=form.name.data,
                          city=form.city.data,
                          address=form.address.data,
                          phone=form.phone.data,
                          state=form.state.data,
                          genres=form.genres.data,
                          website_link=form.website_link.data,
                          facebook_link=form.facebook_link.data,
                          seeking_talent=form.seeking_talent.data,
                          image_link=form.image_link.data,
                          seeking_description=form.seeking_description.data)

            # on successful db insert, flash success
            db.session.add(venue)
            db.session.commit()
            flash('Venue  was successfully listed!')

        except:
            # on unsuccessful db insert, flash an error instead.
            db.session.rollback()
            print(sys.exc_info())
            flash('Venue  could not be listed.', 'error')

        finally:
            # close the db session and redirect to template
            db.session.close()
    else:
        flash('Venue  could not be listed.', 'error')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:

        # Get the Venue to delete and delete
        Venue.query.filter_by(id=venue_id).delete()

        db.session.commit()
        flash('Venue  was successfully deleted!')
    except:
        # if delete fails rollback and flash message
        db.session.rollback()
        flash('Venue  could not be delete.', 'error')
    finally:
        # close db session and render homepage
        db.session.close()
        return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

    data = []
    # get all artists
    artists = db.session.query(Artist.id, Artist.name).all()

    # append artists to data list
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    response = {}

    search_term = request.form['search_term']

    # to enable search all artist names that have the search_term
    search_term = '%'+search_term+'%'

    # search query
    artists = db.session.query(Artist.id, Artist.name).filter(
        Artist.name.ilike(search_term))

    # No of artists
    artists_count = artists.count()

    response = {"count": artists_count}

    response["data"] = []
    # append artist in response
    for artist in artists.all():
        # aggregate number of supcoming shows per artist
        num_upcoming_shows = Show.query.filter(Show.artist_id == artist.id).\
            filter(Show.start_time >= datetime.today().date()).count()

        artist_details = {'id': artist.id, "name": artist.name,
                          "num_upcoming_shows": num_upcoming_shows}

        response["data"].append(artist_details)

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id

    # get the artist
    artist = Artist.query.get(artist_id)

    # Venue details
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,

        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "facebook_link": artist.facebook_link,
        "website": artist.website_link,
        "image_link": artist.image_link
    }
    # Past Shows
    data["past_shows"] = []
    # past shows query
    past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist.id).\
        filter(Show.start_time < datetime.today().date())

    for past_show in past_shows.all():
        past_show_details = {"venue_id": past_show.Venue.id,
                             "venue_name": past_show.Artist.name,
                             "venue_image_link": past_show.Venue.image_link,
                             "start_time": past_show.start_time}
        data["past_shows"].append(past_show_details)

    data["past_shows_count"] = past_shows.count()

    # Artist Upcoming Shows

    data["upcoming_shows"] = []
    upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist.id).\
        filter(Show.start_time >= datetime.today().date())

    for upcoming_show in upcoming_shows.all():
        upcoming_shows_details = {"venue_id": upcoming_show.Venue.id,
                                  "venue_name": upcoming_show.Venue.name,
                                  "venue_image_link": upcoming_show.Venue.image_link,
                                  "start_time": upcoming_show.start_time}
        data["upcoming_shows"].append(upcoming_shows_details)

    data["upcoming_shows_count"] = upcoming_shows.count()

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    # Venue Object
    artist = Artist.query.get(artist_id)
    # Populate form
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    form = ArtistForm(request.form)

    try:

        # validate data
        if form.validate():

            form.populate_obj(artist)
            # on successful db update, flash success

            db.session.commit()
            flash('Artist  was successfully Edited!')
    except:
        # on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        print(sys.exc_info())
        flash('Artist could not be Edited.', 'error')

    finally:
        # close the db session and redirect to venue page
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    # Venue Object
    venue = Venue.query.get(venue_id)
    # Populate form
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    # get record
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form)
    # validate data
    if form.validate():

        try:

            form.populate_obj(venue)
            # on successful db update, flash success

            db.session.commit()
            flash('Venue  was successfully Edited!')
        except:
            # on unsuccessful db insert, flash an error instead.
            db.session.rollback()
            print(sys.exc_info())
            flash('Venue could not be Edited.', 'error')

        finally:
            # close the db session and redirect to venue page
            db.session.close()
    else:
        flash('Venue could not be Edited.', 'error')

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
    form = ArtistForm(request.form)
    if form.validate():

        try:
            # validate data

            artist = Artist(name=form.name.data,
                            city=form.city.data,
                            phone=form.phone.data,
                            genres=form.genres.data,
                            state=form.state.data,
                            website_link=form.website_link.data,
                            facebook_link=form.facebook_link.data,
                            seeking_venue=form.seeking_venue.data,
                            image_link=form.image_link.data,
                            seeking_description=form.seeking_description.data)

            # on successful db insert, flash success
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        except:
            # on unsuccessful db insert, flash an error instead.
            db.session.rollback()
            flash('Artist was not listed', 'error')

        finally:
            # close the db session and redirect to template
            db.session.close()
    else:
        flash('Artist was not listed', 'error')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    data = []

    # query all shows
    shows = Show.query.all()

    # Populate data in dict and append to data list
    for show in shows:
        show_details = {
            "venue_id": show.venue_id,
            "venue_name": show.Venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time}

        data.append(show_details)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm(request.form)
    if form.validate():
        try:
            # validate data

            show = Show(venue_id=form.venue_id.data,
                        artist_id=form.artist_id.data,
                        start_time=form.start_time.data)

            # on successful db insert, flash success
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            # on unsuccessful db insert, flash an error instead.
            db.session.rollback()
            flash('Show was  NOT successfully listed!', 'error')

        finally:
            # close the db session and redirect to template
            db.session.close()
    else:
        flash('Show was successfully listed!')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(401)
def unauthorize_error(error):
    return render_template('errors/401.html'), 401


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(405)
def invalid_method_error(error):
    return render_template('errors/403.html'), 405


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
