
from flask import Flask, jsonify,request, send_from_directory, Response
import json
from flask.views import MethodView
from flask_swagger import swagger
import logging
import os,sys

# prepare nltk
import nltk
nltk.download('punkt') # this one installs rules for punctuation

#inner imports
#sys.path.append(os.path.abspath('..'))
from extractive_summary.Summarizer import Summarizer

app = Flask(__name__, static_url_path='')

class SummaryAPI(MethodView):

    def __init__(self):
        with open('extractive_summary/config.json', 'r') as f:
            config = json.load(f)
            self.summarizer = Summarizer(config)

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
            return json.dumps({'success':False, 'error':'Please provide content, summary length and minimum_distance'}), 404, {'ContentType':'application/json'}


        text = request.json['content']
        length = int(request.json['summary_length'])
        threshold = float(request.json['minimum_distance'])
        method = request.json["method"]

        summary, positions = self.summarizer.summarize(text, method, length, threshold=threshold)

        positions = positions.tolist()
        return json.dumps({'success':True, 'summary':summary, 'positions':positions}), 201, {'ContentType':'application/json'}

summary_view = SummaryAPI.as_view('summaries')
app.add_url_rule('/summarize', view_func=summary_view, methods=["POST"])


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