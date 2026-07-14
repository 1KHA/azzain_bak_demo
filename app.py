from views import blueprint
from flask import Flask, request
from flask_cors import CORS
from celery_tasks import make_celery
from logger import logger

def create_flask_app(name):
    app = Flask(name)

    app.config.from_object("config.Config")
    CORS(app)

    from database import db,ma,migrate
    from helpers.security import jwt
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)

    @app.after_request
    def log_request(response):
        logger.info(f"{request.method} {request.path} → {response.status_code}")
        return response

    app.register_blueprint(blueprint)
    return app

app = create_flask_app(__name__)
celery = make_celery(app)



