from flask import request
from flask.views import MethodView
import json
from server_routes.helpers import create_configured_summarizer, return_json
from tools.exceptions import SummarySizeTooSmall, TextTooLong

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
                method:
                  type: string
                  description: what method is used to create summary
                return_justification:
                  type: boolean
                  description: whether should return ranking for graph based method or visualization for embedding based one.
          201:
            description: Summary created
        """
        params = ['content','summary_length','method','return_justification']
        for param in params:
            if param not in request.json:
                # body should be validated by swagger, but this works also
                return return_json(json.dumps({'success':False, 'error':'Please provide : ' + str(params)}), 404)

        try:
            length = int(request.json['summary_length'])
        except ValueError:
            return return_json(json.dumps({'success': False, 'error': 'Summary length should be integer'}), 404)

        text = request.json['content']
        method = request.json["method"]
        return_justification = request.json['return_justification']

        try:
            if return_justification:
                if method == 'embedding':
                    summary, positions,words, neighbors = self.summarizer.embedding_summary_with_nearest_neighbors(text, length)
                    return return_json(json.dumps(
                        {'success': True, 'summary': summary, 'positions': positions, 'words':words, 'neighbors':neighbors}
                    ), 201)

            summary, positions = self.summarizer.summarize(text, method, length)
            return return_json(json.dumps({'success':True, 'summary':summary, 'positions':positions}), 201)
        except TextTooLong as e:
            return return_json(json.dumps({'success': False, 'error': 'Text is too long for this method'+str(e)+'Please try other one.'}), 404)
        except SummarySizeTooSmall as e:
            return return_json(json.dumps(
                {'success': False, 'error': str(e) + " Please define bigger summary length."}),
                               404)