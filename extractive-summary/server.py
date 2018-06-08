
from flask import Flask, jsonify,request
import json
from flask.views import MethodView
from flask_swagger import swagger

#inner imports
from summary.GraphBasedSummary import GraphBasedSummary

app = Flask(__name__)

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
            # body should be validated by swagger
            return "Please provide content, summary length and minimum_distance"

        text = request.json['content']
        length = int(request.json['summary_length'])
        threshold = float(request.json['minimum_distance'])
        gbs = GraphBasedSummary(text)

        return gbs.summarize(threshold, summary_length=length)

summary_view = SummaryAPI.as_view('summaries')
app.add_url_rule('/summarize', view_func=summary_view, methods=["POST"])

@app.route("/spec")
def spec():
    return jsonify(swagger(app))