import os

from flask import Flask, render_template, request, redirect, url_for
from utils import *
from flask_sqlalchemy import SQLAlchemy

import re

app = Flask(__name__)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

try:
    # get_db_connection = psycopg2.connect(host=HOST, port=PORT, database=DATABASE,
    #                                      user='jkddordfkdcbiu', password=PASSWORD)
    db = SQLAlchemy(app)
    get_db_connection = db.create_engine(SQLALCHEMY_DATABASE_URI,{})
    print("Successfully Connected to Database !")
except Exception as e:
    print("CONNECTION ERROR",e)

@app.route("/youtube-frame-to-play")
def youtube_frame(res='Successful'):
    return render_template("frame.html", remarks=res)

res = 'Waiting to Add !'

@app.route("/", methods=['POST', 'GET'])
def search_add():
    global res
    table_data = get_table_initial_entry(get_db_connection)
    playing = get_table_playing(get_db_connection)

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

@app.route("/addToDatabase")
def get_url_from_user():
    v_id = request.args.get('videoId')
    title = request.args.get('title')
    print('ADDED',v_id,title)

    db_update = add_to_initial_entry(get_db_connection,v_id,title)
    print(db_update)

    return redirect(url_for('search_add'))


@app.route("/firstUpdate", methods=['POST'])
def onPlayerReady():
    print("Here at First Update")
    return "OK"


@app.route("/endUpdate", methods=['POST', 'GET'])
def onPlayerEnd():
    print("Here at Last Update")

    try:
        truncate(get_db_connection,'DELETE FROM playing')
    except Exception as e:
        print("Issue with Truncate !")

    # if len(result) == 0:
    #     return render_template("frame.html", remarks='Not any video in initial table !')
    #
    # remove_entry(""" DELETE FROM initial_entry WHERE id = ?""", result[0][0])
    #
    # if len(result) == 0:
    #     return render_template("frame.html", remarks='Not any video in playing table !')

    to_play = []
    initial_result = get_table_initial_entry(get_db_connection)
    if len(initial_result) == 0:
        videos = get_from_already_played(get_db_connection)
        if len(videos) <= 0:
            return 'TIME TO ADD VIDEOS ! !'

        print(videos)
        to_play.append(videos[0][0])
        to_play.append(videos[0][1])
    else:
        to_play.append(initial_result[0][1])
        to_play.append(initial_result[0][4])
        remove_entry(get_db_connection, 'DELETE FROM initial_entry WHERE id=%s', initial_result[0][0])

    add_to_playing(get_db_connection,to_play[0],to_play[1])

    result = get_table_playing(get_db_connection)
    to_return = [result[-1][1],result[-1][2]]

    add_to_already_played(get_db_connection,to_return[0],to_return[1])

    return to_return[0]

