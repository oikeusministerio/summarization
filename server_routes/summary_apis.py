
from flask import request, render_template, make_response, send_file, Response
from flask.views import MethodView
import json
from server_routes.helpers import create_configured_summarizer, return_json
from extractive_summary.output import SummaryWriter
import imgkit
import tempfile
import base64

from tools.exceptions import SummarySizeTooSmall, TextTooLong

def custom_send_file(file, mimetype, name):
    response = make_response(file)
    response.headers.set('Content-Type', mimetype)
    response.headers.set(
        'Content-Disposition', 'attachment', filename=name)
    return response

def handle_response(return_type, result):
    if return_type == 'json':
        return return_json(json.dumps(result), 201)
    elif return_type == 'html':
        return render_template('multi_file_summary.html', data=result)
    elif return_type == 'docx':
        sw = SummaryWriter(result)
        with tempfile.NamedTemporaryFile(suffix='.docx') as t:
            sw.write_docx(t.name)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            return send_file(
                t.name,
                mimetype=mimetype,
                as_attachment=True,
                attachment_filename='testi.docx'
            )
    elif return_type == 'png':
        html = render_template('base.html', data=result)
        with tempfile.NamedTemporaryFile(suffix='.png') as t:
            imgkit.from_string(html, t.name, css='static/styles.css')
            with open(t.name, 'rb') as image_binary:
                image = base64.b64encode(image_binary.read())
                mimetype = 'image/png'
                return custom_send_file(image, mimetype, 'summary.png')
    else:
        raise ValueError(
            'Given return type ' + str(return_type) + ' unknown. Please choose either json, html, docx or png.')

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
            return return_json(json.dumps({'success': False, 'error': 'Text is too long for this method'+str(e)+'Please split the text.'}), 404)
        except SummarySizeTooSmall as e:
            return return_json(json.dumps(
                {'success': False, 'error': str(e) + " Please define bigger summary length."}),
                               404)


ALLOWED_EXTENSIONS = ['docx','txt', 'pdf']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SummaryFileAPI(MethodView):

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
        return handle_response(return_type, result)

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
            description: the files to upload
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
        return handle_response(return_type, all_summaries)