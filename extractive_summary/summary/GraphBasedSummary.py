import numpy as np
import pandas as pd

from tools.exceptions import SummarySizeTooSmall, TextTooLong
from tools.tools import sentence_tokenize

from gensim.summarization.summarizer import summarize

class GraphBasedSummary:

    max_sentences = 250

    def __init__(self, text, threshold=0.1):
        self.sentences = self.split_document_to_sentences(text)
        N = len(self.sentences)
        if N > GraphBasedSummary.max_sentences:
            raise TextTooLong(" " +  str(N) + " sentences are too many for the graph based method (max "+GraphBasedSummary.max_sentences+").")
        self.dumping_factor = 0.85
        self.threshold = threshold

    def split_document_to_sentences(self, text):
        sentences = sentence_tokenize(text)
        sentences = [s for s in sentences if len(s) > 3]
        # add id to give order for sentences later
        return pd.DataFrame({'position': np.arange(len(sentences)), 'sentence': np.array(sentences)})

    def get_positions(self, sentences):
        get_pos = lambda sent : np.where(self.sentences['sentence'] == sent)
        return [get_pos(s) for s in sentences]

    def summarize(self, word_count=50):
        """
        :param summary_length: number of words to use in summary
        :return: summary
        """
        text = "\n".join(self.sentences['sentence'])
        selected_sentences = summarize(text, word_count=word_count, split=True)
        return selected_sentences, self.get_positions(selected_sentences)