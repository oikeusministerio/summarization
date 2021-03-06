
from flask import make_response, send_file, Response
import json
from extractive_summary.output import SummaryWriter
import tempfile
import os

from extractive_summary.Summarizer import Summarizer

def create_configured_summarizer():
    with open(os.path.abspath('config.json'), 'r') as f:
        config = json.load(f)
        return Summarizer(config)

def return_json(dumped_json, code):
    return dumped_json, code, {'Content-Type': 'application/json; charset=utf-8'}

def custom_send_file(file, mimetype, name):
    response = make_response(file)
    response.headers.set('Content-Type', mimetype)
    response.headers.set(
        'Content-Disposition', 'attachment', filename=name)
    return response

def handle_response(return_type, result):
    writer = SummaryWriter(result)
    with tempfile.NamedTemporaryFile(suffix='.' + return_type) as t:
        writer_func = {'docx': writer.write_docx, 'txt': writer.write_txt}
        writer_func[return_type](t.name)

        mimetypes = {'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     'txt': 'text/plain'}
        return send_file(
            t.name,
            mimetype=mimetypes[return_type],
            as_attachment=True,
            attachment_filename='testi.' + return_type
        )