
import redis
import pickle
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

    def __init__(self, text, dictionary_file=None, dictionary=None):
        assert (dictionary_file != None or dictionary != None)
        if dictionary != None:
            self.dictionary = dictionary
        else:
            self.dictionary = np.load(dictionary_file).item()
        self.reversed_dictionary = dict(zip(self.dictionary.values(), self.dictionary.keys()))
        self.phrases, self.words = self.split_document(text)
        self.r = 0.5 # scaling factor
        self.redis_address = "localhost"
        self.distances, self.distance_index_mapping = self.fetch_distances(self.words)

    def split_document(self, text):
        sentences = sent_tokenize(text, language="finnish")
        words = word_tokenize(text, language="finnish")
        words = np.array([w.lower() for w in words if w.lower() in self.dictionary]) # ATTENTION! Skipping unknown words here.
        words = np.unique(words)  # considering unique is fine, becouse we will consider THE nearests words, so duplicates are useless
        sentences = [s for s in sentences if len(s) > 3]
        return pd.DataFrame({'position': np.arange(len(sentences)), 'sentences': np.array(sentences)}), words

    def nearest_neighbor_objective_function(self, candidate_summary):
        """
        Counts the distance between candidate_summary and document (words of original document).

        :param candidate_summary: list of words => current summary in iterative optimisation process
        :return: negative distance between candidate and phrases
        """
        candidate_summary_indexes = np.array([self.distance_index_mapping[self.dictionary[w.lower()]] \
                                              for w in candidate_summary if w.lower() in self.dictionary])
        if candidate_summary_indexes.shape[0] == 0:
            import pdb;
            pdb.set_trace()
            print(candidate_summary_indexes.shape)
        candidate_document_distances = self.distances[:, candidate_summary_indexes]

        nearests_document_word_distances = candidate_document_distances.min(axis=1)
        # add here scaling function
        return -nearests_document_word_distances.sum()

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
        sentences_left = self.phrases['sentences'].values # U in algorithm
        candidate_summary = np.array([]) # C in algorithm
        candidate_word_count = 0

        while(len(sentences_left) > 0):
            s_candidates = np.array([
                self.nearest_neighbor_objective_function(self.split_sentences(np.array([s]))) / len(s) ** self.r \
                for s in sentences_left])
            s_star_i = s_candidates.argmax()
            s_star = sentences_left[s_star_i]

            if candidate_word_count + len(s_star)  <= summary_size:
                candidate_summary = np.append(candidate_summary, s_star)
                candidate_word_count += len(s_star)

            sentences_left = np.delete(sentences_left, s_star_i)

        # then let's consider sentence, that is the best all alone, algorithm line 6
        sentences_left = self.phrases['sentences'].values
        s_candidates = np.array([
            self.nearest_neighbor_objective_function(self.split_sentences(np.array([s]))) \
            for s in sentences_left if len(s) <= summary_size])
        s_star = sentences_left[s_candidates.argmax()]

        # and now choose eiher the best sentence or combination, algorithm line 7
        if s_candidates.max() > self.nearest_neighbor_objective_function(self.split_sentences(candidate_summary)):
            return s_star
        else:
            return candidate_summary

    def fetch_distances(self, words):
        """
        Connects to redis database, that is supposed to contain distances between all words, and fetches only words needed.
        Vocabulary of each individuel text is supposed to contain so few words that they fit to memory.
        :param words:
        :return: distances and transformations for indexes
        """
        connection = redis.Redis(self.redis_address, db=0)
        indexes = np.array([self.dictionary[w] for w in words])

        N = len(indexes)
        distance_matrix = np.zeros((N,N))

        submatrix_indexes = {}
        for i,ind in enumerate(indexes):
            submatrix_indexes[ind] = i
            b_word_distances = connection.get(ind)
            word_distances = np.array(pickle.loads(b_word_distances))

            distance_matrix[i] = word_distances[0, indexes]

        return distance_matrix, submatrix_indexes