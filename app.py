import os

from flask import Flask, abort, render_template, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import models
from models import Base

DATABASE_URL = os.environ['DATABASE_URL']

# engine = create_engine("postgresql://postgres:postgres@localhost:5432/chinook")
engine = create_engine(DATABASE_URL)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base.query = db_session.query_property()

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
                          
@app.route("/artists", methods= ["GET", "POST"])
def artists():
    if request.method == "GET":
        return get_artists()
    elif request.method == "POST":
        return post_artists()
    abort(405)

def post_artist():
    data = request.json
    new_name = data.get("name")
    if new_name is None:
        abort(404)

    db_session.add(Artist.name = new_name)
    db_session.commit()

    artist = db_session.query(models.Artist).filter(models.Artist.name = new_name).one()

    return jsonify(dict(artist))

def get_artists():
    artists = db_session.query(models.Artist).order_by(models.Artist.name)
    return "<br>".join(
        f"{idx}. {artist.name}" for idx, artist in enumerate(artists)
    )


@app.route("/longest_tracks")
def longest_tracks():
    tracks = db_session.query(models.Track).order_by(models.Track.milliseconds.desc()).limit(10).all()
    return jsonify(dict(row for row in tracks))

@app.route("/longest_tracks_by_artist")
def longest_tracks_by_artist():
    a = request.args

    if ('artist' in a):
        artist = a['artist']
    else:
        raise InvalidUsage('missing artist')

    try:
        tracks = db_session.query(models.Track).filter(models.Track.Album.Artist.name == artist).order_by(models.Track.milliseconds.desc()).limit(10).all()
        print(tracks)
    except:
        return 400

    return jsonify(dict(row for row in tracks))


                          
                          
if __name__ == "__main__":
    app.run(debug=False)
