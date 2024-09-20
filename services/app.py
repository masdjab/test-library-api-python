import os, logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from libs.config import config
from libs.cache import Cache


LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'

def init_flask_app():
  logdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
  if not os.path.isdir(logdir):
    os.mkdir(logdir)

  logger = logging.getLogger(__name__)
  logging.basicConfig(
    filename=os.path.join(logdir, "library-api.log"), 
    level=logging.INFO, 
    format=LOG_FORMAT
  )

  flask_app = Flask(__name__)
  flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.db_url
  return flask_app


app = init_flask_app()
db = SQLAlchemy(app)
migrate = Migrate(app, db)
logger = app.logger
cache = Cache(2000, 800)
