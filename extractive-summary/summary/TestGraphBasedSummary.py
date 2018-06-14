
import numpy as np
import unittest
from .GraphBasedSummary import GraphBasedSummary

class TestGraphBasedSummary(unittest.TestCase):

    def test_cosine_similarity(self):
        """
        https://stackoverflow.com/questions/1746501/can-someone-give-an-example-of-cosine-similarity-in-a-very-simple-graphical-wa
        """
        s1 = np.array("Julie loves me more than Linda loves me".split(' '))
        s2 = np.array("Jane likes me more than Julie loves me".split(' '))
        gbs = GraphBasedSummary("blaa blaa")
        sim = gbs.sentence_cosine_similarity(s1,s2)
        true_value = 0.822
        self.assertLess(abs(sim - true_value), 0.1)

if __name__ == '__main__':
    unittest.main()