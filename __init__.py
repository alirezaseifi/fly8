from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
import rq

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

def create_app(config_class=Config):
    # ...
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)

#create all db tables
@app.before_first_request
def create_tables():
    from models import ContactModel
    db.create_all()

from app import models
