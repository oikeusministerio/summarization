from flask import request
from flask.views import MethodView
import json
from server_routes.helpers import return_json
from extractive_summary.NameExtractor import NameExtractor
from extractive_summary.DocumentParser import DocumentParser
import tempfile

class NamedEntityAPI(MethodView):

    def __init__(self):
        self.name_extractor = NameExtractor()

    def post(self):
        """
        Create a summary for given text.
        ---
        tags:
          - named entities
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
                summary_length:
          201:
            description: Named entities extracted
        """
        params = ['content']
        for param in params:
            if param not in request.json:
                # body should be validated by swagger, but this works also
                return return_json(json.dumps({'success':False, 'error':'Please provide : ' + str(params)}), 404)

        text = request.json['content']
        names_found = self.name_extractor.extract_names({'Teksti': text}, ['Teksti'])
        return return_json(json.dumps({'success': True, 'names': names_found}), 200)
