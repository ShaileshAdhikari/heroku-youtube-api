import hashlib
from datetime import datetime
from youtube_player import db

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    cookie = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=1)
    registered_on = db.Column(db.DateTime, nullable=False,default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.cookie = hashlib.sha256(
            (username + email + str(datetime.now())).encode('utf-8')
        ).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.username

class VideoVault(db.Model):

    __tablename__ = 'video_vault'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    thumbnail = db.Column(db.String(80), unique=True, nullable=False)
    duration = db.Column(db.String(80), unique=True, nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_on = db.Column(db.DateTime, nullable=False)
    last_played_on = db.Column(db.DateTime, nullable=False, default=datetime.now)
    play_count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<VideoVault %r>' % self.name


class InitialEntry(db.Model):

    __tablename__ = 'initial_entry'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    thumbnail = db.Column(db.String(80), unique=True, nullable=False)
    duration = db.Column(db.String(80), unique=True, nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return '<InitialEntry %r>' % self.name

class CurrentlyPlaying(db.Model):

    __tablename__ = 'currently_playing'

    id = db.Column(db.Integer, primary_key=True)
    vault_id = db.Column(db.Integer, db.ForeignKey('video_vault.id'), nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return '<CurrentlyPlaying %r>' % self.video_id