
from flask import Flask, jsonify,request, send_from_directory, send_file
import json
from flask.views import MethodView
from flask_swagger import swagger
import logging
import os,sys
from io import BytesIO
import urllib
import ast
from extractive_summary.summary.result_visualization import visualize_embedding_results
import numpy as np

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
                return_justification:
                  type: boolean
                  description: whether should return ranking for graph based method or visualization for embedding based one.
          201:
            description: Summary created
        """
        params = ['content','summary_length','minimum_distance','method','return_justification']
        for param in params:
            if param not in request.json:
                # body should be validated by swagger, but this works also
                return return_json(json.dumps({'success':False, 'error':'Please provide : ' + str(params)}), 404)

        try:
            length = int(request.json['summary_length'])
            threshold = float(request.json['minimum_distance'])
        except ValueError:
            return return_json(json.dumps({'success': False, 'error': 'Summary length should be integer'}), 404)

        text = request.json['content']
        method = request.json["method"]
        return_justification = request.json['return_justification']

        if return_justification:
            if method == 'embedding':
                summary, positions,words, neighbors = self.summarizer.embedding_summary_with_nearest_neighbors(text, length)
                return return_json(json.dumps(
                    {'success': True, 'summary': summary, 'positions': positions, 'words':words, 'neighbors':neighbors}
                ), 201)
            else:
                summary, positions, ranking = self.summarizer.graph_summary_with_ranking(text, length, threshold)
                return return_json(json.dumps(
                    {'success': True, 'summary': summary, 'positions': positions, 'ranking': ranking}
                ), 201)


        summary, positions = self.summarizer.summarize(text, method, length, threshold=threshold)
        return return_json(json.dumps({'success':True, 'summary':summary, 'positions':positions}), 201)

ALLOWED_EXTENSIONS = ['docx'] # let's add more extensions, like .txt, when they are implemented

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
        consumes:
         - multipart/form-data
        parameters:
          - in: formData
            name: file
            type: file
            required: true
            description: the file to upload
          - in: path
            name: method
            type: string
            required: true
            description: what method is used to create summary
          - in: path
            name: summary_length
            type: int
            required: true
            description: maximum number of characters to use in summary
          - in: path
            name: minimum_distance
            type: float
            required: true
            description: wminimum distance between two sentences. 0.1 seems to be best. Used only with graph based method.

          201:
            description: Summary created
        """

        if 'file' not in request.files:
            return return_json(json.dumps({'success':False, 'error':'There are no file in request.'}), 404)

        file = request.files['file']
        if file.filename == '':
            return return_json(json.dumps({'success': False, 'error': 'No file selected : filename is empty.'}), 404)

        params = ['summary_length', 'minimum_distance', 'method']
        for param in params:
            if param not in request.args:
                # body should be validated by swagger, but this works also
                return return_json(json.dumps({'success': False, 'error': 'Please provide : ' + str(params)}), 404)

        method = request.args.get('method')

        try:
            summary_length = int(request.args.get('summary_length'))
            minimum_distance = float(request.args.get('minimum_distance'))
        except ValueError:
            return return_json(json.dumps({'success': False, 'error': 'Summary length should be integer amd minimum_distance float'}), 404)

        if file and allowed_file(file.filename):
            parser = DocumentParser(file)
            parsed_document, titles = parser.parse()
            summaries = {}
            for title in titles:
                summary, positions = self.summarizer.summarize(" ".join(parsed_document[title]), method, summary_length, threshold=minimum_distance)
                summaries[title] = {'summary':summary,'positions':positions}
            summaries['success'] = True
            summaries['titles'] = titles
            return return_json(json.dumps(summaries), 201)
        else:
            return return_json(json.dumps({'success':False, 'summary':"file extendsion not one of : " + str(ALLOWED_EXTENSIONS), 'positions':[12]}), 404)

class VisualisationEmbeddingAPI(MethodView):

    def __init__(self):
        with open('extractive_summary/config.json', 'r') as f:
            config = json.load(f)
            self.embeddings = np.load(config['embeddings_file'])
            dictionary = np.load(config['dictionary_file']).item()
            self.reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))

    def get(self):
        """
        Create a summary for given text-file.
        ---
        tags:
          - summaries
        parameters:
          - in: path
            name: words
            type: list or array
            required: true
            description: words of original document
          - in: path
            name: neighbors
            type: list or array
            required: true
            description: nearest neighbors of each word in words array
          201:
            description: Summary created
        """
        # check if the post request has the file part
        words = request.args.get('words')
        words = ast.literal_eval(words)
        neighbors = request.args.get('neighbors')
        neighbors = ast.literal_eval(neighbors)

        bytes_io = BytesIO()
        visualize_embedding_results(words, neighbors, self.reverse_dictionary, self.embeddings, bytes_io)
        bytes_io.seek(0)
        return send_file(bytes_io, mimetype='image/png')

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