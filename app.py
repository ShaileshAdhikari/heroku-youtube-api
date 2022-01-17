from flask import Flask, render_template, request, redirect, url_for
from utils import *
import re

app = Flask(__name__)

@app.route("/youtube-frame-to-play")
def youtube_frame(res='Successful'):
    return render_template("frame.html", remarks=res)

res = 'Waiting to Add !'

@app.route("/", methods=['POST', 'GET'])
def search_add():
    global res
    table_data = get_table_initial_entry()
    playing = get_table_playing()

    if request.method == 'GET':
        return render_template("search.html", response='',
                               status=res, songl=table_data,
                               playing = playing)
    if request.method == 'POST':
        vid = request.form['video_url']
        vurl = request.form['video_link']

        if len(vurl) < 10:
            response = get_search_results(vid) if len(vid) > 3 \
                else 'Query should have at least 3 words OR Valid video link  !'
        else:
            VIDEO_ID = vurl.split('/')[-1]
            response = get_video_name(VIDEO_ID) if (len(VIDEO_ID) > 10) & (len(VIDEO_ID) < 12) \
                else 'Invalid video link ! '

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

    db_update = add_to_initial_entry(v_id,title)
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
        truncate('DELETE FROM playing')
    except Exception as e:
        print("Issue with Truncate !")

    # if len(result) == 0:
    #     return render_template("frame.html", remarks='Not any video in initial table !')
    #
    # remove_entry(""" DELETE FROM initial_entry WHERE id = ?""", result[0][0])
    #
    # if len(result) == 0:
    #     return render_template("frame.html", remarks='Not any video in playing table !')

    initial_result = get_table_initial_entry()
    if len(initial_result) == 0:
        return 'Not any video in initial table !'

    add_to_playing(initial_result[0][1],initial_result[0][4])

    result = get_table_playing()
    to_return = [result[-1][1],result[-1][2]]

    remove_entry('DELETE FROM initial_entry WHERE id=%s', initial_result[0][0])

    add_to_already_played(to_return[0],to_return[1])

    return to_return[0]

