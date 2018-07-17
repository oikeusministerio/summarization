
from flask import request, render_template, make_response
from flask.views import MethodView
import json
from server_routes.helpers import create_configured_summarizer, return_json
import base64
import tempfile
import imgkit

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
          - in: return_type
            type: string
            required: true
            description: return summary in either json, html or png. Html and png will be formatted.

          201:
            description: Summary created
        """

        if 'file' not in request.files:
            return return_json(json.dumps({'success':False, 'error':'There are no file in request.'}), 404)

        file = request.files['file']
        if file.filename == '':
            return return_json(json.dumps({'success': False, 'error': 'No file selected : filename is empty.'}), 404)

        params = ['summary_length', 'method', 'return_type']
        for param in params:
            if param not in request.args:
                # body should be validated by swagger, but this works also
                return return_json(json.dumps({'success': False, 'error': 'Please provide : ' + str(params)}), 404)

        method = request.args.get('method')
        return_type = request.args.get('return_type')
        try:
            summary_length = int(request.args.get('summary_length'))
        except ValueError:
            return return_json(json.dumps({'success': False, 'error': 'Summary length should be integer.'}), 404)

        if not file or not allowed_file(file.filename):
            return return_json(json.dumps({'success': False, 'error': "file extendsion not one of : " + \
                                                                      str(ALLOWED_EXTENSIONS),'positions': []}), 404)

        summaries = self.summarizer.summary_from_file(file,method, summary_length)
        result = {}
        result[file.filename] = summaries
        result['filenames'] = [file.filename]
        result['success'] = True

        return_type = request.args.get('return_type')
        print(return_type)
        if return_type == 'json':
            return return_json(json.dumps(result), 201)
        elif return_type == 'html':
            return render_template('multi_file_summary.html', data=result)
        elif return_type == 'png':
            html = render_template('base.html', data=result)
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
            raise ValueError(
                'Given return type ' + str(return_type) + ' unknown. Please choose either json, html or png.')