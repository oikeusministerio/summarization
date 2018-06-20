
import unittest
from flask import Flask
from flask_testing import TestCase
import json

from server import get_app

def post_text(client, text,summary_length,method):
    response = client.post('/summarize',
                            data=json.dumps(
                                {"content": text, "summary_length": summary_length, "minimum_distance": 0.1,
                                 "method": method}),
                            content_type='application/json')
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

if __name__ == '__main__':
    unittest.main()