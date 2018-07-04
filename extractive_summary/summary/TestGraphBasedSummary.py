
import numpy as np
import unittest
from .GraphBasedSummaryOld import GraphBasedSummaryOld
from .GraphBasedSummary import GraphBasedSummary
from tools.tools import load_data
from nltk import word_tokenize

def get_text(i):
    fname = "judgments/data"
    data = load_data(fname, N=(i+1))
    return data.iloc[i]['text']

class TestGraphBasedSummary(unittest.TestCase):

    # test of old class
    def test_old_cosine_similarity(self):
        """
        https://stackoverflow.com/questions/1746501/can-someone-give-an-example-of-cosine-similarity-in-a-very-simple-graphical-wa
        """
        s1 = np.array("Julie loves me more than Linda loves me".split(' '))
        s2 = np.array("Jane likes me more than Julie loves me".split(' '))
        gbs = GraphBasedSummaryOld("blaa blaa")
        sim = gbs.sentence_cosine_similarity(s1,s2)
        true_value = 0.822
        self.assertLess(abs(sim - true_value), 0.1)

    # test of old class
    def test_old_ranking_is_returned(self):
        text = get_text(1)
        summarizer = GraphBasedSummaryOld(text)
        phrases, positions, rankings = summarizer.summarize(summary_length=500, return_ranking=True)
        self.assertEqual(len(phrases), len(positions))
        self.assertEqual(len(positions), len(rankings))

    # test of old class
    def test_old_ranking_indexes_are_valid(self):
        text = get_text(1)
        summarizer = GraphBasedSummaryOld(text)
        phrases, positions, rankings = summarizer.summarize(summary_length=600, return_ranking=True)
        self.assertEqual(len(phrases), len(positions))
        self.assertEqual(len(positions), len(rankings))

        sentences = summarizer.sentences
        self.assertLessEqual(max(positions),len(sentences))
        self.assertLessEqual(max(rankings.index.tolist()),len(sentences))

    def test_summarization(self):
        for text in [get_text(4), get_text(5)]:
            for words in [100,200,500]:
                summarizer = GraphBasedSummary(text)
                sentences, _ = summarizer.summarize(word_count=words)
                summary = " ".join(sentences)
                real_word_count = len([w for w in word_tokenize(summary) if len(w) > 1])
                self.assertLessEqual(real_word_count, words)

if __name__ == '__main__':
    unittest.main()