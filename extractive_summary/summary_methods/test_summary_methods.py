
import pickle
from .embedding import EmbeddingsBasedSummary
import re

import numpy as np
import unittest
from .graphbased import GraphBasedSummary
from tools.tools import load_data
from nltk import word_tokenize

class TestEmbeddingsBasedSummary(unittest.TestCase):

    def test_nearest_neighbor_objective_function(self):
        candidate_summary = np.array([0,2])
        dictionary = {"eka": 0, "toka": 1, "kolmas": 2, "neljäs":3}
        distances = np.array([[0,1,1,1],\
                              [1,0,1,1],\
                              [1,1,0,1],\
                              [1,1,1,0]], dtype=float)
        distance_index_mapping = {i:i for i in [0,1,2,3]}
        text = "eka toka. kolmas neljäs."

        summary = EmbeddingsBasedSummary(text, dictionary=dictionary)
        summary.distances = distances
        summary.distance_index_mapping = distance_index_mapping
        sim = summary.nearest_neighbor_objective_function(candidate_summary)
        self.assertEqual(sim, -4)

        distances *= 2
        distances[0,2] = 1.5
        sim = summary.nearest_neighbor_objective_function(candidate_summary)
        self.assertEqual(sim, -7.5)

        #candidate_summary = ["eka", "kolmas", "neljäs"]
        candidate_summary = np.array([0,2,3])
        distances[:, 3] = 0.5
        sim = summary.nearest_neighbor_objective_function(candidate_summary)
        self.assertEqual(sim, -3.5)

    def test_nearest_neighbors(self):
        distances = np.array([[0, 5, 3, 4], \
                              [1, 0, 2, 1.5], \
                              [2, 1.1, 0, 1], \
                              [3, 1, 0.5, 0]], dtype=float)
        text = "tätä ei testata."
        summary = EmbeddingsBasedSummary(text, dictionary={})
        dist_result, nearest = summary.nearest_neighbors(distances, [0])
        result = distances[:, 0]
        result[0] = 1000
        self.assertTrue((dist_result == result).all())
        self.assertTrue((nearest == 0).all())

        dist_result, nearest = summary.nearest_neighbors(distances, [0,1,2,3])
        self.assertTrue((dist_result == [3,1,1,0.5]).all())
        self.assertTrue((nearest == [2, 0, 3, 2]).all())

    def test_precalcule_sentence_distances(self):
        distances = np.array([[0, 1, 2, 3], \
                              [1, 0, 1.1, 1.5], \
                              [2, 1.1, 0, 0.5], \
                              [3, 1.5, 0.5, 0]], dtype=float)
        text = "tätä ei testata."
        sentences = np.array(['eka toka kolmas','toka kolmas nelkku'])
        vocabulary = ['eka','toka','kolmas','nelkku']
        dictionary = dict(zip(vocabulary, np.arange(len(vocabulary))))
        distance_index_mapping = dict(zip(np.arange(len(vocabulary)), np.arange(len(vocabulary))))
        summarization = EmbeddingsBasedSummary(text, dictionary=dictionary)
        summarization.distance_index_mapping = distance_index_mapping
        summarization.distances = distances
        dist = summarization.precalcule_sentence_distances(sentences)
        self.assertTrue((dist == np.array([-3.6, -3.1])).all())

    def test_modified_greedy_algo(self):
        fname = "judgments/data"
        data = load_data(fname, N=1)
        self.assertIsNotNone(data)
        text = data.iloc[0]['text']
        summarizer = EmbeddingsBasedSummary(text, dictionary_file="embeddings/data/dictionary.npy")
        summarizer.calculate_sentence_lengths()
        sentences, _, nearest_words = summarizer.modified_greedy_algrorithm(200)
        summary = " ".join(sentences).lower()
        only_alphabet = re.compile('^[A-z]+$')
        for word in np.unique(nearest_words):
            if only_alphabet.match(word) and word != '``': # REMOVE THIS LATER, UGLY FIX
                self.assertTrue(word in summary, word)

    def test_precalcule_sentence_indexes(self):
        text = "tätä ei testata."
        dictionary = {'eka':0, 'toka':1}
        summary = EmbeddingsBasedSummary(text, dictionary=dictionary)
        summary.distance_index_mapping = dict(enumerate(range(2)))
        sentences = np.array([
            'Eka toka.',
            'Toka tuntematon.'
        ])
        result = summary.precalcule_sentence_indexes(sentences)
        self.assertTrue((result[0] == np.array([0,1])).all())
        self.assertTrue((result[1] == np.array([1])).all())

def get_text(i):
    fname = "judgments/data"
    data = load_data(fname, N=(i+1))
    return data.iloc[i]['text']

class TestGraphBasedSummary(unittest.TestCase):

    def test_summarization(self):
        for text in [get_text(3), get_text(6)]:
            for words in [100,200,300]:
                summarizer = GraphBasedSummary(text)
                sentences, _ = summarizer.summarize(word_count=words)
                summary = " ".join(sentences)
                real_word_count = len([w for w in word_tokenize(summary) if len(w) > 1])
                self.assertLessEqual(real_word_count, words)

if __name__ == '__main__':
    unittest.main()