
from flask import request
from flask_restplus import Api, Resource, fields
from flask_restful import reqparse
from werkzeug.datastructures import FileStorage

#inner imports
from server_routes.helpers import handle_response

from server_routes.helpers import create_configured_summarizer, return_json
from tools.exceptions import SummarySizeTooSmall, TextTooLong


def configure_summarize_paths(api, ns):
    #'content','summary_length','method'
    copy_paste_summary = api.model('Summarize', {
        'content': fields.String(required=True, description='Text to summarize.'),
        'summary_length': fields.Integer(required=True, description='Summary length should be integer.'),
        'method': fields.String(required=True, description='', choices=('graph', 'embedding')),
    })
    @ns.route('', methods=["post"])
    @ns.response(404, 'summary not found')
    class CopyPasteSummarize(Resource):

        ''' '''
        @ns.doc('post_copy_paste_summarize')
        @ns.expect(copy_paste_summary)
        def post(self):
            ''' '''
            self.summarizer = create_configured_summarizer()
            length = int(request.json['summary_length'])
            text = request.json['content']
            method = request.json["method"]

            try:
                summary, positions = self.summarizer.summarize(text, method, length)
                return return_json(({'success':True, 'summary':summary, 'positions':positions}), 201)
            except TextTooLong as e:
                return return_json(({'success': False, 'error': 'Text is too long for this method'+str(e)+'Please split the text.'}), 404)
            except SummarySizeTooSmall as e:
                return return_json((
                    {'success': False, 'error': str(e) + " Please define bigger summary length."}),
                                   404)


    multi_file_parser = reqparse.RequestParser(bundle_errors=True)
    multi_file_parser.add_argument('summary_length',  type=int, help='Summary length should be integer.', required=True, location='args')
    multi_file_parser.add_argument('method', type=str, choices=('graph', 'embedding'), help="What method to use to summarize, either 'graph' or 'embed'", required=True, location='args')
    multi_file_parser.add_argument('file-0', type=FileStorage, location='files', help="At least one file containing text to handle.", required=True)
    multi_file_parser.add_argument('return_type', type=str, help="Return type to define, what server will return.", required=True, location='args')

    @ns.doc(params={arg.name : arg.help  for arg in multi_file_parser.args})
    @ns.route('/directory', methods=["post"])
    @ns.response(404, 'summary not found')
    class MultiFileSummarize(Resource):
        ''' '''

        @ns.doc('post_file_summarize')
        @ns.expect(multi_file_parser, validate=True)
        def post(self):
            ''' '''
            args = multi_file_parser.parse_args()
            self.summarizer = create_configured_summarizer()
            method = args.get('method')
            summary_length = int(args.get('summary_length'))
            return_type = args.get('return_type')

            all_summaries = {}
            filenames = []
            for file in request.files:
                f = request.files[file]
                file_summary = self.summarizer.summary_from_file(f, method, summary_length)
                all_summaries[f.filename] = file_summary
                filenames.append(f.filename)

            all_summaries['success'] = True
            all_summaries['filenames'] = filenames

            return handle_response(return_type, all_summaries)