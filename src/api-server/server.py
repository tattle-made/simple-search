from controllers.queue_controller import queue_controller
from controllers.mongo_controller import mongo_controller
from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api
from resources.media import Media
from resources.search import Search
from resources.health import Health
from dotenv import load_dotenv
load_dotenv()

queue_controller.connect()
queue_controller.declare_queues()
mongo_controller.connect()

app = Flask(__name__)
CORS(app)
# https://flask-restful.readthedocs.io/en/latest/reqparse.html#error-handling
app.config['BUNDLE_ERRORS'] = True

api = Api(app)

api.add_resource(Health, '/')
api.add_resource(Media, '/media')
api.add_resource(Search, '/search')
api = Api(app, catch_all_404s=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)