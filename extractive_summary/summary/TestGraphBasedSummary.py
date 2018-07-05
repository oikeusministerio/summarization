
import numpy as np
import unittest
from .GraphBasedSummary import GraphBasedSummary
from tools.tools import load_data
from nltk import word_tokenize

def get_text(i):
    fname = "judgments/data"
    data = load_data(fname, N=(i+1))
    return data.iloc[i]['text']

class TestGraphBasedSummary(unittest.TestCase):

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