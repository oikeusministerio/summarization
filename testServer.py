
import unittest
from flask import Flask
from flask_testing import TestCase
import json
from io import BytesIO, StringIO

from server import get_app

def post_text(client, text,summary_length,method):
    response = client.post('/summarize',
                            data=json.dumps(
                                {"content": text, "summary_length": summary_length, "minimum_distance": 0.1,
                                 "method": method}),
                            content_type='application/json')
    return json.loads(response.data.decode('utf8'))

def post_file(client, filename, summary_length, method):
    with open("extractive_summary/" + filename, 'rb') as f:
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

    def test_index_is_rendered(self):
        response = self.client.get("/")

        self.assertTrue('text/html' in response.content_type)

    def test_summarization_embedding(self):
        summary_length = 200
        with open("judgements/data/1985_II10.txt", 'r') as f:
            text = f.read()

        response_json = post_text(self.client, text, summary_length, "embedding")
        summary = response_json['summary']
        first_sentence = summary.split('.')[0]
        self.assertTrue(first_sentence in text)
        self.assertTrue(len(summary) <= summary_length)


    def test_summarization_graph(self):
        summary_length = 350
        with open("judgements/data/1985_II10.txt", 'r') as f:
            text = f.read()

        response_json = post_text(self.client, text, summary_length, "graph")
        summary = response_json['summary']
        first_sentence = summary.split('.')[0]
        self.assertTrue(first_sentence in text)
        self.assertTrue(len(summary) <= summary_length)

    def test_summarization_with_docx(self):
        summary_lengths = [50, 100,200,500]
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
                        self.assertTrue(len(response_json[title]) <= summary_length)
                        summary = response_json[title]['summary']
                        if len(summary) > 0:
                            first_sentence = summary.split('.')[0]
                            self.assertTrue(first_sentence in summary)

if __name__ == '__main__':
    unittest.main()