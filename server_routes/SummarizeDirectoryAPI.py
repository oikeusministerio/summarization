from flask import request
from flask.views import MethodView
import json
from server_routes.helpers import create_configured_summarizer, return_json
import pandas as pd

ALLOWED_EXTENSIONS = ['docx','txt']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SummaryDirectoryAPI(MethodView):

    def __init__(self):
        self.summarizer = create_configured_summarizer()

    def post(self):
        """
        Create a summary for given directory.
        ---
        tags:
          - summaries
        consumes:
         - multipart/form-data
        parameters:
          - in: formData
            name: files
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

        if len(request.files) < 1:
            return return_json(json.dumps({'success':False, 'error':'There are no file in request.'}), 404)

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
            return return_json(
                json.dumps({'success': False, 'error': 'Summary length should be integer amd minimum_distance float'}),404)

        all_summaries = {}
        filenames = []
        for file in request.files:
            f = request.files[file]
            file_summary = self.summarizer.summary_from_file(f, method, summary_length, minimum_distance)
            all_summaries[f.filename] = file_summary
            filenames.append(f.filename)

        all_summaries['success'] = True
        all_summaries['filenames'] = filenames
        return return_json(json.dumps(all_summaries), 201)