
from flask import Flask, jsonify,request, send_from_directory, Response
import json
from flask.views import MethodView
from flask_swagger import swagger

#inner imports
from summary.GraphBasedSummary import GraphBasedSummary

app = Flask(__name__, static_url_path='')

class SummaryAPI(MethodView):

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
              properties:
                content:
                  type: string
                  description: text content
                summary_length:
                  type: int
                  description: maximum number of characters to use in summary
                minimum_distance:
                  type: float
                  description: minimum distance between two sentences. 0.1 seems to be best.
          201:
            description: Summary created
        """
        if 'content' not in request.json or 'summary_length' not in request.json or 'minimum_distance' not in request.json:
            # body should be validated by swagger, but this works also
            return json.dumps({'success':False, 'error':'Please provide content, summary length and minimum_distance'}), 404, {'ContentType':'application/json'}

        text = request.json['content']
        length = int(request.json['summary_length'])
        threshold = float(request.json['minimum_distance'])
        gbs = GraphBasedSummary(text)

        summary, positions = gbs.summarize(threshold, summary_length=length)
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