
import numpy as np
import unittest
from .GraphBasedSummary import GraphBasedSummary
from tools.tools import load_data

def get_text(i):
    fname = "judgements/data"
    data = load_data(fname, N=(i+1))
    return data.iloc[i]['text']

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

    def test_ranking_is_returned(self):
        text = get_text(0)
        summarizer = GraphBasedSummary(text)
        phrases, positions, rankings = summarizer.summarize(summary_length=500)
        self.assertEqual(len(phrases), len(positions))
        self.assertEqual(len(positions), len(rankings))

    def test_ranking_indexes_are_valid(self):
        text = get_text(1)
        summarizer = GraphBasedSummary(text)
        phrases, positions, rankings = summarizer.summarize(summary_length=600)
        self.assertEqual(len(phrases), len(positions))
        self.assertEqual(len(positions), len(rankings))

        sentences = summarizer.sentences
        self.assertLessEqual(max(positions),len(sentences))
        self.assertLessEqual(max(rankings.index.tolist()),len(sentences))


if __name__ == '__main__':
    unittest.main()