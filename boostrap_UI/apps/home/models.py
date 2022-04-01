# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db

from datetime import datetime

class VideoVault(db.Model):

    __tablename__ = 'video_vault'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    thumbnail = db.Column(db.String(80), nullable=False)
    duration = db.Column(db.String(80), nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_played_on = db.Column(db.DateTime, nullable=True, onupdate=datetime.now)
    play_count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<VideoVault %r>' % self.name

class InitialEntry(db.Model):

    __tablename__ = 'initial_entry'

    id = db.Column(db.Integer, primary_key=True)
    vault_id = db.Column(db.Integer, db.ForeignKey('video_vault.id'),nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return '<InitialEntry %r>' % self.vault_id

class CurrentlyPlaying(db.Model):

    __tablename__ = 'currently_playing'

    id = db.Column(db.Integer, primary_key=True)
    vault_id = db.Column(db.Integer, db.ForeignKey('video_vault.id'),nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return '<CurrentlyPlaying %r>' % self.video_id
