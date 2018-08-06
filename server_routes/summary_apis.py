
from flask import request
from flask_restplus import Api, Resource, fields
from flask_restful import abort
from werkzeug.datastructures import FileStorage

#inner imports
from server_routes.helpers import handle_response

from server_routes.helpers import create_configured_summarizer, return_json
from tools.exceptions import SummarySizeTooSmall, TextTooLong


def configure_summarize_paths(api, ns):
    copy_paste_parser = ns.parser()
    copy_paste_parser.add_argument('summary_length', type=int, help='Summary length should be integer.', required=True,location='json')
    copy_paste_parser.add_argument('method', type=str, choices=('graph', 'embedding'),
                                   help="What method to use to summarize, either 'graph' or 'embedding'", required=True,location='json')
    copy_paste_parser.add_argument('content', type=str, help="Text to summarize.", required=True, location="json")

    copy_paste_response = api.model('Summarize response', {
        'summary': fields.String(description="Created summary in plain text."),
        'positions': fields.List(fields.Integer, description='Positions of selected sentences: [3,7,9] means that selected 3th, 7th and 9th sentence of content.')
    })
    @ns.route('', methods=["post"])
    @ns.response(404, 'summary not found')
    class CopyPasteSummarize(Resource):

        @ns.doc('post_copy_paste_summarize')
        @ns.marshal_with(copy_paste_response)
        def post(self):
            """
            Summarizes the given text content with given method.
            """
            args = copy_paste_parser.parse_args()
            self.summarizer = create_configured_summarizer()
            length = int(args['summary_length'])
            text = args['content']
            method = args["method"]


            try:
                summary, positions = self.summarizer.summarize(text, method, length)
                return return_json(({'summary':summary, 'positions':positions}), 201)
            except TextTooLong as e:
                abort(400, error='Text is too long for this method '+str(e)+' Please split the text.')
            except SummarySizeTooSmall as e:
                abort(400, error=str(e) + " Please define bigger summary length.")


    multi_file_parser = api.parser()
    multi_file_parser.add_argument('summary_length',  type=int, help='Summary length should be integer.', required=True, location='args')
    multi_file_parser.add_argument('method', type=str, choices=('graph', 'embedding'), help="What method to use to summarize, either 'graph' or 'embed'", required=True, location='args')
    multi_file_parser.add_argument('file-0', type=FileStorage, location='files', help="At least one file containing text to handle.", required=True)
    multi_file_parser.add_argument('return_type', type=str, choices=('txt', 'docx'), help="Return type to define, what server will return.", required=True, location='args')

    #@ns.doc(params={arg.name : arg.help  for arg in multi_file_parser.args})
    @ns.route('/directory', methods=["post"])
    @ns.response(404, 'summary not found')
    class MultiFileSummarize(Resource):

        @ns.response(200, 'File download : file contains the generated summary. File extension defined by return_type param.')
        @ns.expect(multi_file_parser, validate=True)
        def post(self):
            """
            Summarizes the given files with given method. Each file is summarized separately    .
            """
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