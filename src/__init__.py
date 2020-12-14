from flask import Flask

def create_app():
    flask_app = Flask(__name__)
    flask_app.app_context().push()
    return flask_app
