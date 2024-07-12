from flask import Flask

import os

from app.database import db, migrate
from app.limiter import limiter
from app.caching import cache
from app.swagger_docs import swaggerui_blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.json.sort_keys = False

db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)
cache.init_app(app)

app.register_blueprint(swaggerui_blueprint)

from . import routes, models
