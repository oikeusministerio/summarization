
import numpy as np
import pandas as pd
from nltk import sent_tokenize, word_tokenize
from .EmbeddingsReader import EmbeddingsReader
import sys
import os
sys.path.append(os.path.abspath("../")) # not maybe the best way to structure but MVP
from summarization.tools import word_is_valid

class EmbeddingsBasedSummary:
    """
    This algorithm is following the idea presented in

    Kobayashi, Hayato, Masaki Noguchi, and Taichi Yatsuka.
    "Summarization based on embedding distributions."
    Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing. 2015.
    """

    def __init__(self, text, embeddings):
        self.phrases, self.words = self.split_document(text)
        self.embeddings = embeddings

    def split_document(self, text):
        phrases = sent_tokenize(text, language="finnish")
        words = word_tokenize(text, language="finnish")
        words = np.array([w for w in words if word_is_valid(w)])
        # add id to give order for phrases later
        return pd.DataFrame({'position': np.arange(len(phrases)), 'phrase': np.array(phrases)}), words

    def nearest_neighbor_objective_function(self, candidate_summary):
        """
        Counts the distance between candidate_summary and document (words of original document).

        :param candidate_summary: list of words => current summary in iterative optimisation process
        :return: negative distance between candidate and phrases
        """
        return -sum([self.embeddings.similarity_word_to_text(word, candidate_summary) for word in self.words])

    