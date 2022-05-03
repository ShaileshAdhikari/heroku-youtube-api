# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps.home import blueprint
from flask import render_template, request, jsonify, current_app as app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps import db, socketio
from apps.decorators import check_for_admin
from .models import VideoVault, InitialEntry, CurrentlyPlaying
from .util import (
    get_initial_entry, get_playing, clean_playings, get_video_from_vault,
    db_addition, db_deletion, update_video_vault_count, return_vid, get_search_results,
    get_video_name,insert_to_video_vault,insert_to_initial_entry,get_most_played,
    get_all_from_video_vault
)


@blueprint.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    if request.method == 'GET':
        return render_template(
            'home/index.html', segment='index', user=current_user,
        )
    if request.method == 'POST':
        search_string = request.form['search-box']
        if len(search_string) > 4:
            isURL = return_vid(search_string)
            searchItems = get_search_results(search_string) if isURL == 'InvalidURL' else get_video_name(isURL,db)

            return render_template(
                'home/index.html', segment='search', user=current_user,
                searchItems=searchItems
            )
        else:
            return render_template(
                'home/index.html', segment='index', user=current_user,
                message="Please enter at least 5 characters"
            )

@blueprint.route("/get-song-list", methods=['GET'])
@login_required
def get_song_list():
    table_data = get_initial_entry()
    play_dict = get_playing()[0]
    playing = [play_dict if play_dict is not None else []]
    _most = get_most_played()[0]
    most_played = [_most if _most is not None else []]

    return jsonify({
        'success': True,
        'result': {
            'songList': table_data,
            'playing': playing,
            'mostPlayed': most_played
        }
    })

@blueprint.route('/frame')
@login_required
@check_for_admin
def youtube_frame():
    return render_template('home/frame.html', user=current_user)

@blueprint.route('/vault',methods=['GET'])
@login_required
@check_for_admin
def get_vault_list():
    if request.method == 'GET':
        vault_list = get_all_from_video_vault()
        return jsonify({
            'success': True,
            'result': {
                'vaultList': vault_list
            }
        })


@blueprint.route('/end')
@login_required
def on_player_end():
    try:
        clean_playings(db)
    except Exception as e:
        print("Issue with Truncate !")

    initial_result = get_initial_entry(get_one=True)

    if len(initial_result) == 0:
        # Get video from the Video Vault
        video = list(get_video_from_vault())
        if len(video) > 0:
            video = video[0]
            # Adding to Playing
            if db_addition(
                    db,
                    CurrentlyPlaying(vault_id=video['vault_id'])
            ):
                app.logger.info(f"Added video to play by {current_user.email}")
            else:
                app.logger.error(f"Error adding video to play by {current_user.email}")
                return jsonify({
                    'success': False,
                    'result': {'error': 'Addition Error !'},
                })
        else:
            app.logger.error(f"Error adding video to play by {current_user.email}")
            return jsonify({
                'success': False,
                'result': {'error': 'No Video On Vault !'},
            })

    else:
        initial_result = initial_result[0]
        # remove initial_result video from initial_entry
        if db_deletion(db,
                       InitialEntry.query.where(InitialEntry.vault_id == initial_result['vault_id']).first(),
                       ):
            app.logger.info(f"Deleted Initial Entry by {current_user.email}")

            # add initial_result video to playing
            if db_addition(db,
                           CurrentlyPlaying(vault_id=initial_result['vault_id']),
                           ):
                app.logger.info(f"Added Initial Entry to Playing by {current_user.email}")
            else:
                app.logger.error(f"On adding Initial Entry to Playing by {current_user.email}")
                return jsonify({
                    'success': False,
                    'result': {'error': 'Error on adding video on player !'},
                })
        else:
            app.logger.error(f"On removing from InitialEntry by {current_user.email}")
            return jsonify({
                'success': False,
                'result': {'error': 'Error on updating Initial Playlist !'},
            })

    # get video_id from playing and update vault count
    result = get_playing()[0]
    update_video_vault_count(result['vault_id'], db)

    return jsonify({
        'success': True,
        'result': result['video_id'],
    })


@blueprint.route("/playlist", methods=['POST'])
@login_required
def playlist():
    if request.method == 'POST':
        data = request.get_json()['video']
        videoID = data['id']
        videoName = data['name']
        videoThumbnail = data['thumbnail']
        videoDuration = data['duration']
        addedBy = current_user.get_id()

        result = insert_to_video_vault(
            videoID, videoName, videoThumbnail,
            videoDuration, addedBy, db
        )
        if result['video_id'] and insert_to_initial_entry(result['video_id'], db):
            app.logger.info(f"Added new video by {current_user.email}")
            return jsonify({
                'success': True,
                'result': "Added Successfully",
            })
        else:
            app.logger.error(f"Error adding video by {current_user.email}")
            return jsonify({
                'success': False,
                'result': {'error': 'Error on adding video !'},
            })


@blueprint.route("/remove-get", methods=['GET'])
@login_required
def remove_get():
    if request.method == 'GET':
        result = get_playing()[0]['vault_id']
        try:
            clean_playings(db)
        except Exception as e:
            print("Issue with Truncate !")
        if db_deletion(db,
                       VideoVault.query.where(VideoVault.id == result).first(),
                       ):
            app.logger.info(f"Removed video by {current_user.email}")

            return on_player_end()


@socketio.on('disconnect', namespace='/console')
def disconnect():
    # table_data = get_initial_entry()
    # play_dict = get_playing()[0]
    # playing = [play_dict if play_dict is not None else []]
    # _most = get_most_played()[0]
    # most_played = [_most if _most is not None else []]
    #
    # return render_template(
    #     'home/index.html', segment='index', user=current_user,
    #     songList=table_data, playing=playing, mostPlayed=most_played,
    # )
    return ("Called Disconnect !")

@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
