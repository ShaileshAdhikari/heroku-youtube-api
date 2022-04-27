import os, logging
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')+'?check_same_thread=False'
app.secret_key = 'a0b79ecc3ceca2372f865229192e90fd50f77099fc3868081af8a235f46f38ad'
app.config['SESSION_TYPE'] = 'filesystem'

CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import youtube_player.views

@app.before_first_request
def before_first_request():
    log_level = logging.INFO
    defaultFormatter = logging.Formatter('[%(asctime)s] %(levelname)s in '
                                         'function %(funcName)s: %(message)s')
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)

    root = os.path.dirname(os.path.abspath(__file__))
    logdir = os.path.join(root, 'logs')
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    log_file = os.path.join(logdir, 'app.log')
    handler = logging.FileHandler(log_file)
    handler.setLevel(log_level)
    handler.setFormatter(defaultFormatter)
    app.logger.addHandler(handler)

    app.logger.setLevel(log_level)