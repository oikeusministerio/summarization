
from flask import Flask, jsonify
from flask.views import MethodView
from flask_swagger import swagger

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
              properties:
                content:
                  type: string
                  description: text content
        responses:
          201:
            description: Summary coming
        """
        return "jou"

summary_view = SummaryAPI.as_view('summaries')
app.add_url_rule('/summarize', view_func=summary_view, methods=["POST"])

@app.route("/spec")
def spec():
    return jsonify(swagger(app))