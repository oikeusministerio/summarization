
import numpy as np
import pickle
from redis import Redis
import unittest
from .EmbeddingsBasedSummary import EmbeddingsBasedSummary

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
        connection = Redis(host="localhost", db=0)

        # prepare test db
        distances = [[0,1,2],[3,0,4],[5,6,0]]
        for i, dist in enumerate(distances):
            connection.set(i, pickle.dumps(np.array(dist).reshape(1,-1)))

        text = "eka toka. kolmas eka."
        dictionary = {"eka":0,"toka":1,"kolmas":2}
        summary = EmbeddingsBasedSummary(text, dictionary=dictionary)

        expected_result = np.array(distances)[0:2,0:2]
        sub_distance_mat,_ = summary.fetch_distances(["eka","toka"])

        self.assertTrue((expected_result == sub_distance_mat).all())

if __name__ == '__main__':
    unittest.main()