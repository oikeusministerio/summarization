
import unittest
from unittest.mock import MagicMock
from .Summarizer import Summarizer, ParallelSummary
import itertools
import numpy as np
import time
import json

def create_configured_summarizer():
    with open('config.json', 'r') as f:
        config = json.load(f)
        return Summarizer(config)

class TestSummarizer(unittest.TestCase):

    def test_parallel_summary(self):
        fake_summary = ('Liiba laaba.',[1])
        ids = np.arange(15)
        fake_titles = ['Title' + str(id) for id in ids]
        fake_parsed_document = dict(zip(fake_titles, itertools.repeat('blaa')))
        summarizer = Summarizer({"dictionary_file":None})
        summarizer.summarize = MagicMock(return_value=fake_summary)
        ms = ParallelSummary(summarizer)
        summaries = ms.summarize(fake_parsed_document, fake_titles, None, 10)
        for key in summaries.keys():
            self.assertTrue(summaries[key]['summary'] == fake_summary[0])

    def test_document_parser_time(self):
        tick = time.time()

        with open('extractive_summary/test_files/big_text.txt', 'rb') as file:
            file.filename = 'big_text.txt'
            summarizer = create_configured_summarizer()
            summaries = summarizer.summary_from_file(file, "embed", 15)

        tock = time.time()

        print("time in seconds: " + str(tock - tick))
        self.assertLessEqual(tock - tick, 65)