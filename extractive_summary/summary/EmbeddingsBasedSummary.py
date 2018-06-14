
import numpy as np
import pandas as pd
from nltk import sent_tokenize, word_tokenize
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
        self.r = 0.85 # scaling factor

    def split_document(self, text):
        phrases = sent_tokenize(text, language="finnish")
        words = word_tokenize(text, language="finnish")
        words = np.array([w.lower() for w in words if word_is_valid(w)])
        # add id to give order for phrases later
        return pd.DataFrame({'position': np.arange(len(phrases)), 'phrase': np.array(phrases)}), words

    def nearest_neighbor_objective_function(self, candidate_summary):
        """
        Counts the distance between candidate_summary and document (words of original document).

        :param candidate_summary: list of words => current summary in iterative optimisation process
        :return: negative distance between candidate and phrases
        """
        return -sum([self.embeddings.similarity_word_to_text(word, candidate_summary) for word in self.words])

    def split_sentences(self,sentences):
        """
        :param sentences: array of sentences
        :return: array of words
        """
        return np.hstack(np.array([np.array(s.split()) for s in sentences]))

    def modified_greedy_algrorithm(self, summary_size = 1000):
        """

        Implementation of Algorithm 1 in chapter 3

        :param summary_size: the size of summary to be made
        :return: summary
        """
        phrases_left = self.phrases['phrase'].values # U in algorithm
        candidate_summary = np.array([]) # C in algorithm
        candidate_word_count = 0

        while(len(phrases_left) > 0):
            print(candidate_summary.shape)
            s_candidates = np.array([
                self.nearest_neighbor_objective_function(self.split_sentences(np.append(candidate_summary, s))) / len(s) ** self.r \
                for s in phrases_left])
            s_star_i = s_candidates.argmax()
            s_star = phrases_left[s_star_i]

            if candidate_word_count + len(s_star)  <= summary_size:
                candidate_summary = np.append(candidate_summary, s_star)
                candidate_word_count += len(s_star)

            phrases_left = np.delete(phrases_left, s_star_i)

        # then let's consider sentence, that is the best all alone, algorithm line 6
        s_candidates = np.array([
            self.nearest_neighbor_objective_function(self.split_sentences(np.append(candidate_summary, s))) \
            for s in self.phrases['phrase'].values if len(s) <= summary_size])
        s_star = phrases_left[s_candidates.argmax()]

        # and now choose eiher the best sentence or combination, algorithm line 7
        if s_candidates.max() > self.nearest_neighbor_objective_function(self.split_sentences(candidate_summary)):
            return s_star
        else:
            return candidate_summary