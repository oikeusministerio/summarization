
import unittest
from flask import Flask
from flask_testing import TestCase
import json
from io import BytesIO
from urllib import parse
from tools.tools import load_data
import timeout_decorator

from server import get_app

def post_text(client, text,summary_length,method):
    response = client.post('/summarize',
                            data=json.dumps(
                                {"content": text, "summary_length": summary_length, "minimum_distance": 0.1,
                                 "method": method, 'return_justification': True}),
                            content_type='application/json')
    return json.loads(response.data.decode('utf8'))

def post_file(client, filename, summary_length, method):
    with open("extractive_summary/test_files/" + filename, 'rb') as f:
        text = f.read()
        data = dict(
            file=(BytesIO(text), filename),
        )
    response = client.post('/summarize/file?summary_length=' + str(summary_length) \
                                + '&minimum_distance=0.1' \
                                + '&method=' + method, data=data, content_type='multipart/form-data')
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
        response_json = post_text(self.client, text, summary_length, "embedding")
        summary = response_json['summary']
        first_sentence = summary.split('.')[0]
        self.assertTrue(first_sentence in text)

    def test_summarization_graph(self):
        summary_length = 350
        with open('short_test_judgment.txt') as f:
            text = f.read()
        response_json = post_text(self.client, text, summary_length, "graph")
        self.assertTrue('summary' in response_json)
        summary = response_json['summary']
        first_word = summary.split(' ')[0]
        self.assertTrue(first_word in summary)

    def test_summarization_with_docx(self):
        summary_lengths = [100,200,500]
        methods = ["embedding","graph"]
        filenames = ["testi.docx", "testi3.docx"]
        for summary_length in summary_lengths:
            for method in methods:
                for filename in filenames:
                    print(summary_length)
                    print(method)
                    print(filename)
                    response_json = post_file(self.client, filename, summary_length, method)
                    self.assertTrue(response_json['success'])
                    self.assertTrue('titles' in response_json )
                    for title in response_json['titles']:
                        summary = response_json[title]['summary']
                        if len(summary) > 0:
                            first_word = summary.split(' ')[0]
                            self.assertTrue(first_word in summary)

    def test_summarization_with_txt(self):
        summary_lengths = [100,200,500]
        methods = ["embedding","graph"]
        filenames = ["normal_text.txt"]
        for summary_length in summary_lengths:
            for method in methods:
                for filename in filenames:
                    print(summary_length)
                    print(method)
                    print(filename)
                    response_json = post_file(self.client, filename, summary_length, method)
                    self.assertTrue(response_json['success'])
                    self.assertTrue('titles' in response_json )
                    for title in response_json['titles']:
                        summary = response_json[title]['summary']
                        if len(summary) > 0:
                            first_sentence = summary.split('.')[0]
                            self.assertTrue(first_sentence in summary)
    #
    # def test_visualisation(self):
    #     response = self.client.get('/visualize/embeddings?words=' + parse.quote(str([1,2,3,4]), safe='~()*!.\'') + \
    #                                '&neighbors=' + parse.quote(str([1,2,3,4]), safe='~() *!.\''))
    #
    #     self.assertIsNotNone(response.data)

if __name__ == '__main__':
    unittest.main()