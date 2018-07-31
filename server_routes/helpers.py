
from flask import  render_template, make_response, send_file
import json
from extractive_summary.output import SummaryWriter
import imgkit
import tempfile
import base64

from extractive_summary.Summarizer import Summarizer

def create_configured_summarizer():
    with open('config.json', 'r') as f:
        config = json.load(f)
        return Summarizer(config)

def return_json(dumped_json, code):
    return dumped_json, code, {'ContentType': 'application/json'}

def custom_send_file(file, mimetype, name):
    response = make_response(file)
    response.headers.set('Content-Type', mimetype)
    response.headers.set(
        'Content-Disposition', 'attachment', filename=name)
    return response

def handle_response(return_type, result):
    if return_type == 'json':
        return return_json(result, 201)
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