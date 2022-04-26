# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required,current_user
from jinja2 import TemplateNotFound

from .models import VideoVault, InitialEntry, CurrentlyPlaying
from .util import get_initial_entry, get_playing

@blueprint.route('/index')
@login_required
def index():
    table_data = get_initial_entry()
    play_dict = get_playing()[0]
    playing = [play_dict if play_dict is not None else []]

    return render_template('home/index.html',
                           segment='index',
                           user = current_user,
                           songList = table_data,
                           playing = playing,
                           searchItems = [],
                           mostPlayed = [],
                           )


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
