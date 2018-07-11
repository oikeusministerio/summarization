
from flask import Flask, jsonify,request, send_from_directory, send_file
from flask_swagger import swagger
import logging

# prepare nltk
import nltk
nltk.download('punkt') # this one installs rules for punctuation

#inner imports
from server_routes.SummaryAPI import SummaryAPI
from server_routes.SummaryFromFileAPI import SummaryFromFileAPI
from server_routes.VisualisationEmbeddingAPI import VisualisationEmbeddingAPI

app = Flask(__name__, static_url_path='')

UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

summary_view = SummaryAPI.as_view('summaries')
file_summary_view = SummaryFromFileAPI.as_view("summaries from file")
visualisation_view = VisualisationEmbeddingAPI.as_view("visualisation")
app.add_url_rule('/summarize', view_func=summary_view, methods=["POST"])
app.add_url_rule('/summarize/file', view_func=file_summary_view, methods=["POST"])
app.add_url_rule('/visualize/embeddings', view_func=visualisation_view, methods=["GET"])

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

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

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')

def get_app():
    return app