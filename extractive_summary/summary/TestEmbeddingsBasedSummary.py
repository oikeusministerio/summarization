
import numpy as np
import unittest
from .EmbeddingsBasedSummary import EmbeddingsBasedSummary
from .EmbeddingsReader import EmbeddingsReader

def euclidean_distance(a,b):
    return np.sqrt(np.sum((a - b)**2))

def setup_embeddings_reader_mock(embed, dictionary):
    em = EmbeddingsReader(embed_file=None, dico_file=None)
    em.embeddings = embed
    em.dictionary = dictionary
    return em

class TestEmbeddingsBasedSummary(unittest.TestCase):

    def test_embedding_similarity_word_to_word(self):
        embed = np.array([[1, 2, 3], \
                          [4, 5, 6], \
                          [7, 8, 9]])
        dictionary = {"eka": 0, "toka": 1, "kolmas": 2}
        em = setup_embeddings_reader_mock(embed,dictionary)

        expedted_result = euclidean_distance(embed[0,:], embed[1,:])
        sim = em.similarity_word_to_word("eka", "toka")
        diff = abs(sim - expedted_result)
        self.assertLess(diff, 0.001)

    def test_embedding_similarity_word_to_text(self):
        embed = np.array([[1, 2, 3], \
                          [4, 5, 6], \
                          [7, 8, 9]])
        dictionary = {"eka": 0, "toka": 1, "kolmas": 2}
        em = setup_embeddings_reader_mock(embed, dictionary)
        word = "toka"
        text = ["eka","kolmas"]
        expected_result = min(euclidean_distance(embed[1,:],embed[0,:]),euclidean_distance(embed[1,:], embed[2,:]))

        sim = em.similarity_word_to_text(word,text)
        diff = abs(sim - expected_result)
        self.assertLess(diff, 0.001)

    def test_nearest_neighbor_objective_function(self):
        embed = np.array([[1, 2, 3], \
                          [4, 5, 6], \
                          [7, 8, 9], \
                          [-1, -1.5, -2.5]])
        dictionary = {"eka": 0, "toka": 1, "kolmas": 2, "neljäs":3}
        em = setup_embeddings_reader_mock(embed, dictionary)

        candidate_summary = ["eka", "kolmas"]
        text = "eka toka. kolmas neljäs."

        expected_result = euclidean_distance(embed[0,:], embed[0,:]) \
                          + min(euclidean_distance(embed[1,:], embed[0,:]), euclidean_distance(embed[1,:], embed[2,:])) \
                          + min(euclidean_distance(embed[2,:], embed[0,:]), euclidean_distance(embed[2,:], embed[2,:])) \
                          + min(euclidean_distance(embed[3,:], embed[0,:]), euclidean_distance(embed[3,:], embed[2,:]))
        expected_result = -expected_result

        summary = EmbeddingsBasedSummary(text,em)
        sim = summary.nearest_neighbor_objective_function(candidate_summary)
        diff = abs(sim - expected_result)
        print(diff)
        self.assertLess(diff, 0.001)

if __name__ == '__main__':
    unittest.main()