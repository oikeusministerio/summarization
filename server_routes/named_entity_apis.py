from flask import request, make_response, after_this_request, render_template
from flask.views import MethodView
import json
from server_routes.helpers import return_json
from extractive_summary.NameExtractor import NameExtractor
from extractive_summary.parsing import DocumentParser
import tempfile
import requests
import base64
import os

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
        params = ['content','return_type']
        for param in params:
            if param not in request.json:
                # body should be validated by swagger, but this works also
                return return_json(json.dumps({'success':False, 'error':'Please provide : ' + str(params)}), 404)

        text = request.json['content']
        return_type = request.json['return_type']
        try:
            names_found,_ = self.name_extractor.extract_names(text)
            if return_type == 'png':
                graph_data = {}
                graph_data['copy pastettu teksti'] = names_found
                graph_data['filenames'] = ['copy pastettu teksti']
                with tempfile.NamedTemporaryFile(suffix='.gv') as tmp_file:
                    image_file = self.name_extractor.create_graph(tmp_file.name, graph_data)

                    with open(image_file, 'rb') as image_binary:
                        image = base64.b64encode(image_binary.read())

                        @after_this_request # delete .pdf file after sent, .gv file is temporary and will be deleted automatically
                        def remove_file(response):
                            try:
                                os.remove(image_file)
                            except Exception as error:
                                print("Error removing or closing downloaded file handle", error)
                            return response

                        response = make_response(image)
                        response.headers.set('Content-Type', 'image/png')
                        response.headers.set(
                            'Content-Disposition', 'attachment', filename='named_entity_graph.png')
                        return response
            else:
                return return_json(json.dumps({'success': True, 'names': names_found}), 200)
        except requests.exceptions.ConnectionError as e:
            msg = 'Please ensure that dependency parser is running and the correct port has been configured.'
            return return_json(json.dumps({'success': False, 'names': [], 'error': msg}), 500)

class NamedEntityDirectoryAPI(MethodView):

    def __init__(self):
        self.name_extractor = NameExtractor()

    def post(self):
        """
        Create a summary for given text.
        ---
        tags:
         - multipart/form-data
        parameters:
          - in: formData
            name: files
            type: file
            required: true
            description: the files to upload

          201:
            description: Named entities extracted
        """
        params = ['return_type']
        for param in params:
            if param not in request.args:
                # body should be validated by swagger, but this works also
                return return_json(json.dumps({'success':False, 'error':'Please provide : ' + str(params)}), 404)

        return_type = request.args['return_type']
        filenames = []
        file_contents = {}
        for file_id in request.files:
            file = request.files[file_id]
            parser = DocumentParser(file)
            if '.docx' in file.filename:
                text = parser.read_docx_document()
            elif '.txt' in file.filename:
                text = parser.read_txt_document()
            elif '.pdf' in file.filename:
                text = parser.read_pdf_document()
            else:
                continue; # cannot handle this type of file
                
            filenames.append(file.filename)
            file_contents[file.filename] = text

        try:
            results = self.name_extractor.extract_names_directory(file_contents, filenames)
            graph_data = {}
            for i, filename in enumerate(filenames):
                graph_data[filename] = results[i]
            graph_data['filenames'] = filenames

            if return_type == 'png':
                with tempfile.NamedTemporaryFile(suffix='.gv') as tmp_file:
                    image_file = self.name_extractor.create_graph(tmp_file.name, graph_data)

                    with open(image_file, 'rb') as image_binary:
                        image = base64.b64encode(image_binary.read())

                        @after_this_request # delete image_file after sent, .gv file is temporary file and will be deleted automatically
                        def remove_file(response):
                            try:
                                os.remove(image_file)
                            except Exception as error:
                                print("Error removing or closing downloaded file handle", error)
                            return response

                        response = make_response(image)
                        response.headers.set('Content-Type', 'image/png')
                        response.headers.set(
                            'Content-Disposition', 'attachment', filename='named_entity_graph.png')
                        return response
            else:
                return render_template('named_entities.html', data=graph_data)
                #return return_json(json.dumps({'success': True, 'names': names_found}), 200)
        except requests.exceptions.ConnectionError as e:
            msg = 'Please ensure that dependency parser is running and the correct port has been configured.'
            return return_json(json.dumps({'success': False, 'names': [], 'error': msg}), 500)