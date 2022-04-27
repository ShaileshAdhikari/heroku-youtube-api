# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from turbo_flask import Turbo
import os,logging


db = SQLAlchemy()
login_manager = LoginManager()
turbo = Turbo()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module(f'apps.{module_name}.routes')
        app.register_blueprint(module.blueprint)

def set_logger(app):
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

def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()
        set_logger(app)

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    turbo.init_app(app)

    return app
