
from flask import Flask, jsonify,request, send_from_directory, send_file
from flask_swagger import swagger
import logging

# prepare nltk
import nltk
nltk.download('punkt') # this one installs rules for punctuation

#inner imports
from server_routes.summary_apis import SummaryAPI, SummaryFileAPI, SummaryDirectoryAPI
from server_routes.visualisation_apis import VisualisationEmbeddingAPI
from server_routes.named_entity_apis import NamedEntityAPI, NamedEntityDirectoryAPI

app = Flask(__name__, static_url_path='')

UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

summary_view = SummaryAPI.as_view('summaries')
file_summary_view = SummaryFileAPI.as_view("summaries from file")
directory_view = SummaryDirectoryAPI.as_view("summarize directory")
visualisation_view = VisualisationEmbeddingAPI.as_view("visualisation")

named_entity_view = NamedEntityAPI.as_view("named entities")
named_entities_dir_view = NamedEntityDirectoryAPI.as_view("named entities from directory")

app.add_url_rule('/summarize', view_func=summary_view, methods=["POST"])
app.add_url_rule('/summarize/file', view_func=file_summary_view, methods=["POST"])
app.add_url_rule('/summarize/directory', view_func=directory_view, methods=["POST"])
app.add_url_rule('/visualize/embeddings', view_func=visualisation_view, methods=["GET"])

app.add_url_rule('/entities', view_func=named_entity_view, methods=["POST"])
app.add_url_rule('/entities/directory', view_func=named_entities_dir_view, methods=["POST"])

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/node_modules/<path:path>')
def send_node_modules(path):
    return send_from_directory('static/node_modules', path)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route("/spec")
def spec():
    return jsonify(swagger(app))

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
#    header['Access-Control-Allow-Methods'] = 'POST, GET'
    header['Access-Control-Allow-Headers'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')

def get_app():
    return app