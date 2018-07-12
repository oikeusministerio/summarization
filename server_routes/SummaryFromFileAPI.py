
from flask import request
from flask.views import MethodView
import json
from server_routes.helpers import create_configured_summarizer, return_json

ALLOWED_EXTENSIONS = ['docx','txt']

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
            summaries = self.summarizer.summary_from_file(file,method, summary_length, minimum_distance)
            result = {}
            result[file.filename] = summaries
            result['filenames'] = [file.filename]
            result['success'] = True
            return return_json(json.dumps(result), 201)
        else:
            return return_json(json.dumps({'success':False, 'error':"file extendsion not one of : " + str(ALLOWED_EXTENSIONS), 'positions':[]}), 404)