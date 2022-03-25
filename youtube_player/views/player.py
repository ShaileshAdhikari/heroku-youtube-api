from flask import session, request, render_template, jsonify
from youtube_player import app, db
from .helpers import *
from youtube_player.decorators import logged_in

@app.route("/youtube-frame-to-play")
def youtube_frame(res='Successful'):
    return render_template("frame.html", remarks=res)

@app.route("/playlist", methods=['GET','POST'])
@logged_in
def playlist():
    if request.method == 'GET':
        result = get_initial_entry()
        app.logger.info(f"Getting Values from Initial Entry by {session['email']}")
        return jsonify({
                'success': True,
                'result':{'data': result},
            })

    if request.method == 'POST':
        data = request.get_json()
        videoID = data['id']
        videoName = data['name']
        videoThumbnail = data['thumbnail']
        videoDuration = data['duration']
        addedBy = User.query.where(User.email == session['email']).first().id

        result = insert_to_video_vault(
            videoID, videoName, videoThumbnail,
            videoDuration, addedBy, db
        )
        if result['video_id'] and insert_to_initial_entry(result['video_id'],db):
            app.logger.info(f"Added new video by {session['email']}")
            return jsonify({
                'success': True,
                'result':{'message': 'Added Successfully !'},
            })
        else:
            app.logger.error(f"Error adding video by {session['email']}")
            return jsonify({
                'success': False,
                'result':{'error': 'Addition Error !'},
            })


@app.route("/playing", methods=['GET'])
@logged_in
def playing():
    if request.method == 'GET':
        result = get_playing()
        # get mac address of the device
        print(request.remote_addr)
        app.logger.info(f"Getting Current Playing by {session['email']}")
        return jsonify({
                'success': True,
                'result':{'data': result},
            })

@app.route("/search",methods=['GET'])
@logged_in
def search():
    if request.method == 'GET':
        query = request.args.get('q')
        result = get_search_results(query)
        return jsonify({
                'success': True,
                'result':{'data': result},
            })


@app.route("/link",methods=['GET'])
@logged_in
def link():
    if request.method == 'GET':
        query = request.args.get('q')
        result = get_video_name(return_vid(query))
        return jsonify({
                'success': True,
                'result':{'data': result},
            })

@app.route("/end", methods=['GET'])
def on_player_end():
    try:
        clean_playings(db)
    except Exception as e:
        print("Issue with Truncate !")

    initial_result = get_initial_entry(get_one=True)

    if len(initial_result) == 0:
        # Get video from the Video Vault
        video = get_video_from_vault()
        if video is not None:
            # Adding to Playing
            if db_addition(
                CurrentlyPlaying(vault_id=initial_result.vault_id),
                db
            ):
                app.logger.info(f"Added video to play by {session['email']}")
            else:
                app.logger.error(f"Error adding video to play by {session['email']}")
                return jsonify({
                    'success': False,
                    'result':{'error': 'Addition Error !'},
                })
        else:
            app.logger.error(f"Error adding video to play by {session['email']}")
            return jsonify({
                'success': False,
                'result':{'error': 'No Video On Vault !'},
            })

    else:
        initial_result = initial_result[0]
        # remove initial_result video from initial_entry
        if db_deletion(db,
            InitialEntry.query.where(InitialEntry.vault_id == initial_result['vault_id']).first(),
        ):
            app.logger.info(f"Deleted Initial Entry by {session['email']}")

            # add initial_result video to playing
            if db_addition(db,
                CurrentlyPlaying(vault_id=initial_result['vault_id']),
            ):
                app.logger.info(f"Added Initial Entry to Playing by {session['email']}")
            else:
                app.logger.error(f"On adding Initial Entry to Playing by {session['email']}")
                return jsonify({
                    'success': False,
                    'result':{'error': 'Error on adding video on player !'},
                })
        else:
            app.logger.error(f"On adding Removing from InitialEntry by {session['email']}")
            return jsonify({
                'success': False,
                'result':{'error': 'Error on updating Initial Playlist !'},
            })

    # get video_id from playing and update vault count
    result = get_playing()[0]
    update_video_vault_count(result['vault_id'],db)

    return result['video_id']

# @app.route("/most-played", methods=['GET'])
# @logged_in
# def get_most_played():
#     if request.method == 'GET':
#         result = most_played(get_db_connection)
#         return to_json(result)
#

# @app.route("/user", methods=['POST'])
# def user():
#     if request.method == 'POST':
#         data = request.get_json()
#         token = data['token']
#         return get_user_details(get_db_connection,token)
# # _____________________________________________________________
#
# @app.route("/user/change", methods=['POST'])
# def change_email():
#     if request.method == 'POST':
#         data = request.get_json()
#         token = data['token']
#         new_name = data['name']
#         return change_user_name(get_db_connection,token,new_name)
#
# @app.route("/remove", methods=['DELETE'])
# def remove():
#     if request.method == 'DELETE':
#         id = request.args.get('id')
#         return remove_entry(
#             get_db_connection,
#             'DELETE FROM initial_entry WHERE video_id=%s',
#             id,
#         )
#
# # _______________________________________________________________
#
# @app.route("/", methods=['POST', 'GET'])
# def search_add():
#     global res
#     table_data = to_json(initial_table_getall(get_db_connection))
#     playing = [dict(table_playing(get_db_connection))
#                if table_playing(get_db_connection) is not None else []]
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