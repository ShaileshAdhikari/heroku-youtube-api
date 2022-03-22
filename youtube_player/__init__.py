import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.secret_key = 'a0b79ecc3ceca2372f865229192e90fd50f77099fc3868081af8a235f46f38ad'
app.config['SESSION_TYPE'] = 'filesystem'

CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import youtube_player.views