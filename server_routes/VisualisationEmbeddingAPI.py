
from flask import request, send_file
from flask.views import MethodView
import json
from extractive_summary.summary.result_visualization import visualize_embedding_results
import numpy as np
from io import BytesIO
import ast

class VisualisationEmbeddingAPI(MethodView):

    def __init__(self):
        with open('extractive_summary/config.json', 'r') as f:
            config = json.load(f)
            self.embeddings = np.load(config['embeddings_file'])
            dictionary = np.load(config['dictionary_file']).item()
            self.reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))

    def get(self):
        """
        Create a summary for given text-file.
        ---
        tags:
          - summaries
        parameters:
          - in: path
            name: words
            type: list or array
            required: true
            description: words of original document
          - in: path
            name: neighbors
            type: list or array
            required: true
            description: nearest neighbors of each word in words array
          201:
            description: Summary created
        """
        # check if the post request has the file part
        words = request.args.get('words')
        words = ast.literal_eval(words)
        neighbors = request.args.get('neighbors')
        neighbors = ast.literal_eval(neighbors)

        bytes_io = BytesIO()
        visualize_embedding_results(words, neighbors, self.reverse_dictionary, self.embeddings, bytes_io)
        bytes_io.seek(0)
        return send_file(bytes_io, mimetype='image/png')