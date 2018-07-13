from flask import request, render_template, send_file, make_response
from flask.views import MethodView
import json
from server_routes.helpers import create_configured_summarizer, return_json
import imgkit
import tempfile
import io
import base64

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
          - in: return_type
            type: string
            required: true
            description: return summary in either json, html or png. Html and png will be formatted.

          201:
            description: Summary created
        """

        if len(request.files) < 1:
            return return_json(json.dumps({'success':False, 'error':'There are no file in request.'}), 404)

        params = ['summary_length', 'method', 'return_type']
        for param in params:
            if param not in request.args:
                # body should be validated by swagger, but this works also
                return return_json(json.dumps({'success': False, 'error': 'Please provide : ' + str(params)}), 404)

        method = request.args.get('method')

        try:
            summary_length = int(request.args.get('summary_length'))
        except ValueError:
            return return_json(
                json.dumps({'success': False, 'error': 'Summary length should be integer amd minimum_distance float'}),404)

        all_summaries = {}
        filenames = []
        for file in request.files:
            f = request.files[file]
            file_summary = self.summarizer.summary_from_file(f, method, summary_length)
            all_summaries[f.filename] = file_summary
            filenames.append(f.filename)

        all_summaries['success'] = True
        all_summaries['filenames'] = filenames

        return_type = request.args.get('return_type')
        print(return_type)
        if return_type == 'json':
            return return_json(json.dumps(all_summaries), 201)
        elif return_type == 'html':
            return render_template('multi_file_summary.html', data=all_summaries)
        elif return_type == 'png':
            html = render_template('base.html', data=all_summaries)
            with tempfile.NamedTemporaryFile(suffix='.png') as t:
                imgkit.from_string(html, t.name, css='static/styles.css')
                with open(t.name, 'rb') as image_binary:
                    image = base64.b64encode(image_binary.read())
                    response = make_response(image)
                    response.headers.set('Content-Type', 'image/png')
                    response.headers.set(
                        'Content-Disposition', 'attachment', filename='summary.png')
                    return response
        else:
            raise ValueError('Given return type ' + str(return_type) + ' unknown. Please give either json, html or png.')