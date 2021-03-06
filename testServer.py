
import unittest
from flask import Flask
from flask_testing import TestCase
import json
from io import BytesIO
from urllib import parse
from tools.tools import load_data
import timeout_decorator
import imghdr
import tempfile

from restful_api import get_app

def post_text(client, text,summary_length,method):
    response = client.post('/summarize',
                            data=json.dumps(
                                {"content": text, "summary_length": summary_length,
                                 "method": method, 'return_justification': True}),
                            content_type='application/json')
    return json.loads(response.data.decode('utf8')), response

def post_file(client, filename, summary_length, method, return_type):
    with open("extractive_summary/test_files/" + filename, 'rb') as f:
        text = f.read()
        data = dict(
            file=(BytesIO(text), filename),
        )
    response = client.post('/summarize/file?summary_length=' + str(summary_length) \
                                + '&method=' + method
                                + '&return_type=' + return_type, data=data, content_type='multipart/form-data')
    return json.loads(response.data.decode('utf8')), response

def post_multiple_files(client, filenames, summary_length, method, return_type):
    data = dict()
    for i, filename in enumerate(filenames):
        with open("extractive_summary/test_files/" + filename, 'rb') as f:
            text = f.read()
            data['file-'+str(i)]=(BytesIO(text), filename)
    response = client.post('/summarize/directory?summary_length=' + str(summary_length) \
                                + '&method=' + method
                                + '&return_type=' + return_type, data=data, content_type='multipart/form-data')

    return response

def decode_json(response):
    return json.loads(response.data.decode('utf8'))

class TestServer(TestCase):

    def create_app(self):
        app = get_app()
        app.config['TESTING'] = True
        return app

    @timeout_decorator.timeout(2)
    def test_index_is_rendered(self):
        response = self.client.get("/")

        self.assertTrue('text/html' in response.content_type)

    def test_summarization_embedding(self):
        text = load_data("judgments/data/", N=10).iloc[8]['text']
        summary_length = 200
        response_json,_ = post_text(self.client, text, summary_length, "embedding")
        summary = response_json['summary']
        first_sentence = summary.split('.')[0]
        self.assertTrue(first_sentence in text)

    def test_summarization_graph(self):
        summary_length = 350
        with open('extractive_summary/test_files/short_test_judgment.txt') as f:
            text = f.read()
        response_json,_ = post_text(self.client, text, summary_length, "graph")
        self.assertTrue('summary' in response_json)
        summary = response_json['summary']
        first_word = summary.split(' ')[0]
        self.assertTrue(first_word in summary)

    def test_summarization_with_docx(self):
        summary_lengths = [50,100,200]
        methods = ["embedding","graph"]
        filenames = ["testi.docx", "testi3.docx"]
        for summary_length in summary_lengths:
            for method in methods:
                print(summary_length)
                print(method)
                response = post_multiple_files(self.client, filenames, summary_length, method, 'txt')
                self.assertEquals(response.status_code, 200)
                # more things could be tested, but as the result is validated manually, let's not use more time for unittesting

    def test_summarization_with_txt(self):
        summary_lengths = [50, 100,200]
        methods = ["embedding","graph"]
        filenames = ["normal_text.txt"]
        for summary_length in summary_lengths:
            for method in methods:
                print(summary_length)
                print(method)
                response = post_multiple_files(self.client, filenames, summary_length, method, 'txt')
                self.assertEquals(response.status_code, 200)

    def test_toolong_exception(self):
        filename = 'too_long_text.txt'
        with open('extractive_summary/test_files/' + filename) as f:
            text = f.read()
            _,response = post_text(self.client, text, 10, "graph")
            self.assertEquals(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()