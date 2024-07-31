from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.models import db

def createApp():
	app = Flask(__name__)
	app.config.from_object(LocalDevelopmentConfig)
	app.secret_key = "S3CR3T :)"
	db.init_app(app)
	app.app_context().push()
	return app

app = createApp()

from application.views import *

if(__name__ == "__main__"):
	app.run(port=5001,debug=True)
