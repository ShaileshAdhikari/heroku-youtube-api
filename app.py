import json
from flask import Flask, render_template, request, redirect, url_for, Response
from utils import *
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
try:
    db = SQLAlchemy(app)
    get_db_connection = db.create_engine(SQLALCHEMY_DATABASE_URI,{})
    print("Successfully Connected to Database !")
except Exception as e:
    print("CONNECTION ERROR",e)
    raise ConnectionError("Could not connect to database")

res = 'Waiting to Add !'

@app.route("/youtube-frame-to-play")
def youtube_frame(res='Successful'):
    return render_template("frame.html", remarks=res)

@app.route("/playlist", methods=['GET','POST'])
def playlist():
    if request.method == 'GET':
        result = initial_table_getall(get_db_connection)
        return to_json(result)

    if request.method == 'POST':
        data = request.get_json()
        vId = data['id']
        vName = data['name']
        vThumb = data['thumbnail']
        vDuration = data['duration']

        result = add_to_initial_entry(get_db_connection, vId, vName, vDuration, vThumb)

        return Response(result)

@app.route("/playing", methods=['GET'])
def playing():
    if request.method == 'GET':
        result = table_playing(get_db_connection)
        # get mac address of the device
        print(request.remote_addr)
        return dict(result)

@app.route("/search",methods=['GET'])
def search():
    if request.method == 'GET':
        query = request.args.get('q')
        result = get_search_results(query)
        return Response(json.dumps(result,default=str),
                        mimetype='application/json')


@app.route("/link",methods=['GET'])
def link():
    if request.method == 'GET':
        query = request.args.get('link')
        result = get_video_name(return_vid(query))
        return Response(json.dumps(result,default=str),
                        mimetype='application/json')

@app.route("/most-played", methods=['GET'])
def get_most_played():
    if request.method == 'GET':
        result = most_played(get_db_connection)
        return to_json(result)

@app.route("/end", methods=['GET'])
def on_player_end():
    try:
        truncate(get_db_connection,'DELETE FROM playing')
    except Exception as e:
        print("Issue with Truncate !")

    initial_result = initial_table_gettop(get_db_connection)

    if initial_result is None:
        videos = get_from_already_played(get_db_connection)
        if videos is None:
            return 'TIME TO ADD VIDEOS ! !'

        videos = dict(videos)
        add_to_playing(get_db_connection, videos['id'], videos['name'],
                       videos['duration'],videos['thumbnail'])

        # result = dict(table_playing(get_db_connection))
        #
        # update_already_played(get_db_connection, result['id'])

    else:
        initial_result = dict(initial_result)
        remove_entry(get_db_connection, 'DELETE FROM initial_entry WHERE video_id=%s', initial_result['id'])

        add_to_playing(get_db_connection,initial_result['id'], initial_result['name'],
                       initial_result['duration'],initial_result['thumbnail'])

    result = dict(table_playing(get_db_connection))

    add_to_already_played(get_db_connection,result['id'], result['name'],
                          result['duration'],result['thumbnail'])

    return result['id']
# _____________________________________________________________

@app.route("/user", methods=['GET'])
def user():
    pass

@app.route("/remove", methods=['DELETE'])
def remove():
    if request.method == 'DELETE':
        id = request.args.get('id')
        return remove_entry(
            get_db_connection,
            'DELETE FROM initial_entry WHERE video_id=%s',
            id,
        )

# _______________________________________________________________

@app.route("/", methods=['POST', 'GET'])
def search_add():
    global res
    table_data = to_json(initial_table_getall(get_db_connection))
    playing = [dict(table_playing(get_db_connection))
               if table_playing(get_db_connection) is not None else []]

    if request.method == 'GET':
        return render_template("search.html", response='',
                               status=res, songl=table_data,
                               playing = playing)
    if request.method == 'POST':
        searchQ = request.form['search']
        vLink= request.form['vLink']

        if (len(searchQ) | len(vLink)) == 0:
            response = "Please enter 'SEARCH STRING' of 'VIDEO URL' !"
        elif len(vLink) == 0:
            response = get_search_results(searchQ) if len(searchQ) > 3 else 'Query should have at least 3 words !'
        elif len(searchQ) == 0:
            vId = return_vid(vLink)
            response = 'Invalid Video Link !' if vId == "INVALID URL" else get_video_name(vId)
        else:
            response = "I don't know what happen !"

        res = 'Successfully Added Last One !'
        # return redirect(url_for('search_add',response = response))
        return render_template("search.html", response=response,
                               songl=table_data, status='Click To Add !',
                               playing = playing)
#