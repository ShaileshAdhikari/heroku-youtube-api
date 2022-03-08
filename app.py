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
        return to_json(result)

@app.route("/search",methods=['POST'])
def search():
    if request.method == 'POST':
        query = request.args.get('q')
        result = get_search_results(query)
        return Response(json.dumps(result,default=str),
                        mimetype='application/json')


@app.route("/link",methods=['POST'])
def link():
    if request.method == 'POST':
        query = request.args.get('link')
        result = get_video_name(return_vid(query))
        return Response(json.dumps(result,default=str),
                        mimetype='application/json')

@app.route("/getMostPlayed", methods=['GET'])
def get_most_played():
    if request.method == 'GET':
        result = get_most_played(get_db_connection)
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

        result = dict(table_playing(get_db_connection))

        update_already_played(get_db_connection, result['id'])

    else:
        initial_result = dict(initial_result)
        remove_entry(get_db_connection, 'DELETE FROM initial_entry WHERE video_id=%s', initial_result['id'])

        add_to_playing(get_db_connection,initial_result['id'], initial_result['name'],
                       initial_result['duration'],initial_result['thumbnail'])

        result = dict(table_playing(get_db_connection))

        add_to_already_played(get_db_connection,result['id'], result['name'],
                              result['duration'],result['thumbnail'])

    return result['id']

# _______________________________________________________________

# @app.route("/", methods=['POST', 'GET'])
# def search_add():
#     global res
#     table_data = get_table_initial_entry(get_db_connection)
#     playing = get_table_playing(get_db_connection)
#
#     if request.method == 'GET':
#         return render_template("search.html", response='',
#                                status=res, songl=table_data,
#                                playing = playing)
#     if request.method == 'POST':
#         searchQ = request.form['search']
#         vLink= request.form['vLink']
#
#         if (len(searchQ) | len(vLink)) == 0:
#             response = "Please enter 'SEARCH STRING' of 'VIDEO URL' !"
#         elif len(vLink) == 0:
#             response = get_search_results(searchQ) if len(searchQ) > 3 else 'Query should have at least 3 words !'
#         elif len(searchQ) == 0:
#             vId = return_vid(vLink)
#             response = 'Invalid Video Link !' if vId == "INVALID URL" else get_video_name(vId)
#         else:
#             response = "I don't know what happen !"
#
#         res = 'Successfully Added Last One !'
#         # return redirect(url_for('search_add',response = response))
#         return render_template("search.html", response=response,
#                                songl=table_data, status='Click To Add !',
#                                playing = playing)
#
# @app.route("/addToDatabase")
# def get_url_from_user():
#     v_id = request.args.get('videoId')
#     title = request.args.get('title')
#     print('ADDED',v_id,title)
#
#     db_update = add_to_initial_entry(get_db_connection,v_id,title)
#     print(db_update)
#
#     return redirect(url_for('search_add'))
#
#
# @app.route("/endUpdate", methods=['POST', 'GET'])
# def onPlayerEnd():
#     print("Here at Last Update")
#
#     try:
#         truncate(get_db_connection,'DELETE FROM playing')
#     except Exception as e:
#         print("Issue with Truncate !")
#
#     to_play = []
#     initial_result = get_table_initial_entry(get_db_connection)
#     if len(initial_result) == 0:
#         videos = get_from_already_played(get_db_connection)
#         if len(videos) <= 0:
#             return 'TIME TO ADD VIDEOS ! !'
#
#         print(videos)
#         to_play.extend((videos[0][0], videos[0][1]))
#
#         add_to_playing(get_db_connection, to_play[0], to_play[1])
#
#         result = get_table_playing(get_db_connection)
#         to_return = [result[-1][1], result[-1][2]]
#
#         update_already_played(get_db_connection, to_play[0])
#
#     else:
#         to_play.extend((initial_result[0][1], initial_result[0][4]))
#         remove_entry(get_db_connection, 'DELETE FROM initial_entry WHERE id=%s', initial_result[0][0])
#
#         add_to_playing(get_db_connection,to_play[0],to_play[1])
#
#         result = get_table_playing(get_db_connection)
#         to_return = [result[-1][1],result[-1][2]]
#
#         add_to_already_played(get_db_connection,to_return[0],to_return[1])
#
#     return to_return[0]