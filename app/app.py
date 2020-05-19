from flask import Flask

from .models import db
from .views import api_views


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:rlatnals1!@database-1.csam73rge1ra.ap-northeast-2.rds.amazonaws.com/ideas_assign'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.app_context().push()
    db.init_app(app)
    db.create_all()

    app.register_blueprint(api_views)

    return app







