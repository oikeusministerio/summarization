
import unittest
from unittest.mock import MagicMock
from .Summarizer import Summarizer, MultithreadSummary
import itertools
import numpy as np

class TestSummarizer(unittest.TestCase):

    def test_multithread_summary(self):
        fake_summary = ('Liiba laaba.',[1])
        ids = np.arange(15)
        fake_titles = ['Title' + str(id) for id in ids]
        fake_parsed_document = dict(zip(fake_titles, itertools.repeat('blaa')))
        summarizer = Summarizer({"dictionary_file":None})
        summarizer.summarize = MagicMock(return_value=fake_summary)
        ms = MultithreadSummary(summarizer)
        summaries = ms.summarize(fake_parsed_document, fake_titles, None, 10, 0.1)
        for key in summaries.keys():
            self.assertTrue(summaries[key]['summary'] == fake_summary[0])