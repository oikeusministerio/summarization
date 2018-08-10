
import sys
from flask import Flask, request
from flask_restplus import Api, Resource, fields
import logging

# prepare nltk
import nltk
nltk.download('punkt') # this one installs rules for punctuation

#inner imports
from server_routes.summary_apis import configure_summarize_paths
from server_routes.named_entity_apis import configure_named_entities_paths

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


api = Api(app, version='1.0', title='NLP-application',
    description='App can create extractive summarizes and extract named entities for finnish documents.',
)

configure_summarize_paths(api, api.namespace('summarize', description='Summarize operations'))
configure_named_entities_paths(api, api.namespace('entities', description='NER operations'))

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

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
#    header['Access-Control-Allow-Methods'] = 'POST, GET'
    header['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')

def get_app():
    return app