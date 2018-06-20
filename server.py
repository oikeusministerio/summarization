
from flask import Flask, jsonify,request, send_from_directory, Response
import json
from flask.views import MethodView
from werkzeug.utils import secure_filename
from flask_swagger import swagger
import logging
import os,sys

# prepare nltk
import nltk
nltk.download('punkt') # this one installs rules for punctuation

#inner imports
from extractive_summary.Summarizer import Summarizer
from extractive_summary.DocumentParser import DocumentParser

app = Flask(__name__, static_url_path='')

UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_configured_summarizer():
    with open('extractive_summary/config.json', 'r') as f:
        config = json.load(f)
        return Summarizer(config)

def return_json(dumepd_json, code):
    return dumepd_json, code, {'ContentType': 'application/json'}

class SummaryAPI(MethodView):

    def __init__(self):
        self.summarizer = create_configured_summarizer()

    def post(self):
        """
        Create a summary for given text.
        ---
        tags:
          - summaries
        parameters:
          - in: body
            name: body
            schema:
              id: Text
              required:
                - content
                - summary_length
                - method
              properties:
                content:
                  type: string
                  description: text content
                summary_length:
                  type: int
                  description: maximum number of characters to use in summary
                minimum_distance:
                  type: float
                  description: minimum distance between two sentences. 0.1 seems to be best. Used only with graph based method.
                method:
                  type: string
                  description: what method is used to create summary
          201:
            description: Summary created
        """
        if 'content' not in request.json or 'summary_length' not in request.json or 'minimum_distance' not in request.json or 'method' not in request.json:
            # body should be validated by swagger, but this works also
            return return_json(json.dumps({'success':False, 'error':'Please provide content, summary length, minimum_distance and method.'}), 404)

        try:
            length = int(request.json['summary_length'])
            threshold = float(request.json['minimum_distance'])
        except ValueError:
            return return_json(json.dumps({'success': False, 'error': 'Summary length should be integer'}), 404)

        text = request.json['content']
        method = request.json["method"]

        summary, positions = self.summarizer.summarize(text, method, length, threshold=threshold)

        positions = positions.tolist()
        return return_json(json.dumps({'success':True, 'summary':summary, 'positions':positions}), 201)

ALLOWED_EXTENSIONS = ['doc'] # let's add more extensions, like .txt and .docx, when they are implemented

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SummaryFromFileAPI(MethodView):

    def __init__(self):
        self.summarizer = create_configured_summarizer()

    def post(self):
        """
        Create a summary for given text-file.
        ---
        tags:
          - summaries
        parameters:
          - in: body
            name: body
            schema:
              id: Text
              required:
                - content
                - summary_length
                - method
              properties:
                content:
                  type: file
                  description: file that contains text
                summary_length:
                  type: int
                  description: maximum number of characters to use in summary
                minimum_distance:
                  type: float
                  description: minimum distance between two sentences. 0.1 seems to be best. Used only with graph based method.
                method:
                  type: string
                  description: what method is used to create summary
          201:
            description: Summary created
        """
        # check if the post request has the file part
        #import pdb
        #pdb.set_trace()
        if 'file' not in request.files:
            return return_json(json.dumps({'success':False, 'error':'There are no file in request.'}), 404)

        file = request.files['file']
        if file.filename == '':
            return return_json(json.dumps({'success': False, 'error': 'No file selected : filename is empty.'}), 404)

        if file and allowed_file(file.filename):
            parser = DocumentParser(file)
            parsed_document, titles = parser.parse()
            summaries = {}
            for title in titles:
                summary, positions = self.summarizer.summarize(" ".join(parsed_document[title]), 100, threshold=0.1)
                summaries[title] = {'summary':summary,'positions':positions}
            summaries['success'] = True
            return return_json(json.dumps(summaries), 201)
        else:
            return return_json(json.dumps({'success':False, 'summary':"file extendsion not one of : " + ALLOWED_EXTENSIONS, 'positions':[12]}), 404)


summary_view = SummaryAPI.as_view('summaries')
file_summary_view = SummaryFromFileAPI.as_view("summaries from file")
app.add_url_rule('/summarize', view_func=summary_view, methods=["POST"])
app.add_url_rule('/summarize/file', view_func=file_summary_view, methods=["POST"])

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