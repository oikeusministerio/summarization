
import numpy as np
import pickle
import redis
import unittest
from unittest.mock import patch
from .EmbeddingsBasedSummary import EmbeddingsBasedSummary

class RedisMock:

    def __init__(self):
        self.data = {}
        self.distances = [[0, 11, 2], [3, 0, 4], [5, 6, 0]]
        for i, dist in enumerate(self.distances):
            self.set(i, pickle.dumps(np.array(dist).reshape(1, -1)))

    def set(self,key, val):
        self.data[key] = val

    def get(self, key):
        return self.data[key]

def mock_redis_client(a,b):
    return RedisMock()

class TestEmbeddingsBasedSummary(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestEmbeddingsBasedSummary, self).__init__(*args, **kwargs)
        self.test_redis = 1 # by default it is 0, so let's reserve 0 for production use ans 1 for testing
        # https://github.com/andymccurdy/redis-py

    def test_nearest_neighbor_objective_function(self):
        pass # TEST THIS ONE TOO
        candidate_summary = ["eka", "kolmas"]
        text = "eka toka. kolmas neljäs."


        #summary = EmbeddingsBasedSummary(text)
        #sim = summary.nearest_neighbor_objective_function(candidate_summary)
        #diff = abs(sim)
        #print(diff)
        #self.assertLess(diff, 0.001)

    def test_fetch_distances(self):
        text = "eka toka. kolmas eka."
        dictionary = {"eka":0,"toka":1,"kolmas":2}
        summary = EmbeddingsBasedSummary(text, dictionary=dictionary, redis_client_constructor=RedisMock)

        expected_result = np.array(RedisMock().distances)[0:2,0:2]
        sub_distance_mat,_ = summary.fetch_distances(["eka","toka"])
        self.assertTrue((expected_result == sub_distance_mat).all())

if __name__ == '__main__':
    unittest.main()