from flask import request, make_response, after_this_request, send_file
from server_routes.helpers import return_json
from extractive_summary.ner_extracting import NameExtractor
from extractive_summary.parsing import DocumentParser, replace_words_in_txt
from extractive_summary.output import SummaryWriter
from flask_restplus import Api, Resource, fields
from flask_restful import reqparse

import tempfile
import requests
import base64
import os

ACCEPTED_RETURN_TYPES = ['docx', 'txt']

def configure_named_entities_paths(api, ns):

    ner_text_parser = ns.parser()
    ner_text_parser.add_argument('content', type=str, help='Text where named entities are extracted', required=True, location='json')
    ner_text_parser.add_argument('return_type', type=str, help="Return type to define, what server will return.", \
                                 required=True, location='json', choices=ACCEPTED_RETURN_TYPES)

    @ns.route('', methods=["post"])
    @ns.response(404, 'ner not found')
    class NamedEntityAPI(Resource):

        @ns.doc('post_copy_paste_ner')
        @ns.expect(ner_text_parser)
        def post(self):
            """
            Searches named entities from the given text.
            Using Finnish-dependency parser.
            (https://en.wikipedia.org/wiki/Named-entity_recognition)
            """
            self.name_extractor = NameExtractor()
            args = ner_text_parser.parse_args()
            text = args['content']
            return_type = args['return_type']
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
                    return return_json({'success': True, 'names': names_found}, 200)
            except requests.exceptions.ConnectionError as e:
                msg = 'Please ensure that dependency parser is running and the correct port has been configured.'
                return return_json({'success': False, 'names': [], 'error': msg}, 500)


    ner_file_parser = ns.parser()
    ner_file_parser.add_argument('file-0', type=str, help='At least one file where named entities are extracted', required=True,
                                 location='files')
    ner_file_parser.add_argument('return_type', type=str, help="Return type to define, what server will return.",
                                 required=True, location='args')
    ner_file_parser.add_argument('person_ids', type=bool, help="Should we search person ids as well?.",
                                 required=True, location='args')

    @ns.route('/directory', methods=["post"])
    @ns.response(404, 'ner not found')
    class NamedEntityDirectoryAPI(Resource):

        @ns.doc('post_file_ner')
        @ns.expect(ner_file_parser)
        def post(self):
            """
            Searches named entities from the given files.
            Using Finnish-dependency parser.
            (https://en.wikipedia.org/wiki/Named-entity_recognition)
            """
            self.name_extractor = NameExtractor()
            args = ner_file_parser.parse_args()

            return_type = args['return_type']
            search_person_ids = args['person_ids']

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
                max_words = 100 if return_type == 'png' else 1000
                results = self.name_extractor.extract_names_directory(file_contents, filenames, search_person_ids, names_max_N=max_words)
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
                    return return_json({'success': True, 'names': graph_data}, 200)
            except requests.exceptions.ConnectionError as e:
                msg = 'Please ensure that dependency parser is running and the correct port has been configured.'
                return return_json({'success': False, 'names': [], 'error': msg}, 500)



    replace_parser = ns.parser()
    replace_parser.add_argument('file-0', type=str, help='At least one file with text to replace.',
                                 required=True, location='files')
    replace_parser.add_argument('return_type', type=str, help="Return type to define, what server will return.",
                                 required=True, location='args',
                                 choices=ACCEPTED_RETURN_TYPES)
    replace_parser.add_argument('nerlist', type=str, help="Words that should be replaced.",required=True, location='args')
    replace_parser.add_argument('substitutes', type=str, help="What words to use when replacing..", required=True,
                                location='args')
    @ns.route('/replace', methods=["post"])
    @ns.response(404, 'ner not found')
    class ReplaceWordsAPI(Resource):

        @ns.doc('replace_ners')
        @ns.expect(replace_parser)
        def post(self):
            args = replace_parser.parse_args()
            word_list = args['nerlist']
            word_list =  [w[1:-1].strip() for w in word_list[1:-1].split(',')]

            substitutes = args['substitutes']
            substitutes = [w[1:-1].strip() for w in substitutes[1:-1].split(',')]

            return_type = args['return_type']
            file = request.files['file-0']
            parser = DocumentParser(file)
            if '.docx' in file.filename:
                parsed_document, titles = parser.parse_docx_file()
            elif '.txt' in file.filename:
                parsed_document, titles = parser.parse_txt_file()
            elif '.pdf' in file.filename:
                parsed_document, titles = parser.parse_pdf_file()

            replaced_parsed = replace_words_in_txt(parsed_document, titles, word_list, substitutes)
            replaced_parsed['titles'] = titles

            output = {}
            output['output.docx'] = replaced_parsed
            output['filenames'] = ['output.docx']

            writer = SummaryWriter(output)
            with tempfile.NamedTemporaryFile(suffix='.' + return_type) as t:
                writer_func = {'docx' : writer.write_docx, 'txt': writer.write_txt}
                writer_func[return_type](t.name)

                mimetypes = {'docx' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             'txt' : 'text/plain'}
                return send_file(
                    t.name,
                    mimetype=mimetypes[return_type],
                    as_attachment=True,
                    attachment_filename='testi.' + return_type
                )