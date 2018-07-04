
import numpy as np
import pandas as pd
from nltk import word_tokenize
from sklearn.metrics.pairwise import euclidean_distances
import json
import time

from tools.exceptions import SummarySizeTooSmall
from tools.tools import sentence_tokenize

class EmbeddingsBasedSummary:
    """
    This algorithm is following the idea presented in

    Kobayashi, Hayato, Masaki Noguchi, and Taichi Yatsuka.
    "Summarization based on embedding distributions."
    Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing. 2015.
    """

    def __init__(self, text, dictionary_file=None, dictionary=None, redis_client_constructor=None):
        assert (dictionary_file != None or dictionary != None)
        if dictionary != None:
            self.dictionary = dictionary
        else:
            self.dictionary = np.load(dictionary_file).item()
        self.reversed_dictionary = dict(zip(self.dictionary.values(), self.dictionary.keys()))
        self.sentences, self.words = self.split_document(text)
        self.r = 0.75  # scaling factor, must be positive
        # when searching argmax, indexes with this value are not selected
        # becouse it is so big
        self.max_distance = -10000000
        with open('extractive_summary/config.json', 'r') as f:
            config = json.load(f)
            self.embeddings_file = config["embeddings_file"]
            self.embeddings = np.load(self.embeddings_file)
            tic = time.time()
            self.distances, self.distance_index_mapping = self.calculate_distances(self.words)
            self.reversed_distance_index_mapping = dict(zip(self.distance_index_mapping.values(), \
                                                            self.distance_index_mapping.keys()))
            toc = time.time()
            print("calculating distances took " + str(1000 * (toc - tic)))

    def split_document(self, text, minimum_sentence_length=5):
        sentences = sentence_tokenize(text)
        words = word_tokenize(text, language="finnish")
        words = np.array([w.lower() for w in words if w.lower() in self.dictionary]) # ATTENTION! Skipping unknown words here.
        words = np.unique(words)  # considering unique is fine, becouse we will consider THE nearests words, so duplicates are useless
        words = np.array([w for w in words if len(w) > 1])
        sentences = [s for s in sentences if len(s) >= minimum_sentence_length]

        sentences_without_newlines = []
        for s in sentences:
            s = s.strip()
            if "\n" in s:
                for split in s.split("\n"):
                    split = split.strip()
                    if len(split) >= minimum_sentence_length:
                        sentences_without_newlines.append(split)
            else:
                sentences_without_newlines.append(s)

        sentences = np.array(sentences_without_newlines)
        return pd.DataFrame({'position': np.arange(len(sentences)), 'sentences': sentences}), words

    def nearest_neighbors(self, distances, candidate_summary_indexes):
        index_mapping = dict(enumerate(candidate_summary_indexes))
        candidate_document_distances = distances[:, candidate_summary_indexes]
        # before selecting minimun distances, let's avoid selecting, that the nearest one is the point himself
        cand_sums = candidate_document_distances[candidate_summary_indexes]
        np.fill_diagonal(cand_sums, 1000)  # let's put big value so that diagonal will not be chosen
        candidate_document_distances[candidate_summary_indexes] = cand_sums
        nearests = candidate_document_distances.argmin(axis=1)
        distances = candidate_document_distances.min(axis=1)
        return distances, np.vectorize(index_mapping.get)(nearests) #np.array([index_mapping[i] for i in nearests])

    def nearest_neighbor_objective_function(self, candidate_summary_words):
        """
        Counts the distance between candidate_summary and document (words of original document).

        :param candidate_summary: list of words => current summary in iterative optimisation process
        :return: negative distance between candidate and sentences
        """
        if candidate_summary_words.shape[0] == 0:
            return self.max_distance
        try:
            nearests_document_word_distances, _ = self.nearest_neighbors(self.distances, candidate_summary_words.astype(int))
            return -nearests_document_word_distances.sum()
        except Exception:
            print("Error with " + str(candidate_summary_words))

    def precalcule_sentence_distances(self, sentences_left):
        sentence_word_indexes = self.precalcule_sentence_indexes(sentences_left)
        calcul_distance = lambda indexes : self.nearest_neighbor_objective_function(indexes)
        sentence_distances = np.vectorize(calcul_distance)(sentence_word_indexes)
        sentence_length = np.vectorize(len)(sentences_left)
        return sentence_distances, sentence_length

    def precalcule_sentence_indexes(self, sentences):
        assert len(sentences) > 0, "Provide at least one sentence."
        filter_dictionary_words = lambda sentence: np.array([w for w in word_tokenize(sentence.lower(), language="finnish") if w in self.dictionary])
        get_index = lambda word : self.distance_index_mapping[self.dictionary[word]]
        get_sentence_indexes = lambda sentence: np.vectorize(get_index, otypes=[np.ndarray])(filter_dictionary_words(sentence))
        return np.vectorize(get_sentence_indexes,otypes=[np.ndarray])(sentences)

    def modified_greedy_algrorithm(self, summary_size):
        """

        Implementation of Algorithm 1 in chapter 3

        :param summary_size: the size of summary to be made
        :return: summary
        """
        #sentences_left = self.sentences['sentences'].values # U in algorithm
        #sentences_left = np.array(self.sentences.index.tolist())  # U in algorithm
        N = self.sentences.shape[0]
        print("precalcule")
        sentence_indexes = self.precalcule_sentence_indexes(self.sentences['sentences'].values)
        sentence_distances, sentence_lengths = self.precalcule_sentence_distances(self.sentences['sentences'].values)
        candidate_summary = np.array([], dtype=int) # C in algorithm
        handled = np.array([], dtype=int)  # (C \ handled) in algorithm, in other words : list of indexes not in C (C is thing of algiruthm)
        candidate_summary_words = np.array([], dtype=int)
        candidate_char_count = 0
        print("iterate")
        while(handled.shape[0] < N):
            s_candidates = np.array([
                self.nearest_neighbor_objective_function(
                    np.append(candidate_summary_words, sentence_indexes[i])
                ) / (sentence_lengths[i] ** self.r)
                if i not in handled else 1000
                for i in range(N)])
            distance_min_border = s_candidates.min() - 1000  # indexes with this value cannot be maximum
            s_candidates[s_candidates == 1000] = distance_min_border # this way we dont choose same twice
            s_star_i = s_candidates.argmax()
            s_star = self.sentences['sentences'][s_star_i]

            if candidate_char_count + len(s_star)  <= summary_size:
                candidate_summary = np.append(candidate_summary, s_star_i)
                candidate_char_count += len(self.sentences['sentences'].iloc[s_star_i])
                candidate_summary_words = np.append(candidate_summary_words, sentence_indexes[s_star_i])

            handled = np.append(handled, s_star_i)

        # then let's consider sentence, that is the best all alone, algorithm line 6
        s_candidates = np.array([sentence_distances[i] if sentence_lengths[i] <= summary_size else self.max_distance \
                                for i in range(len(sentence_distances))])
        s_star_i = s_candidates.argmax()

        if len(candidate_summary) == 0: # summary_size smaller than any of sentences
            return np.array([]),np.array([]), np.array([])

        # and now choose eiher the best sentence or combination, algorithm line 7
        if s_candidates.max() > self.nearest_neighbor_objective_function(candidate_summary_words):
            final_summary = np.array([s_star_i])
        else:
            final_summary = candidate_summary

        final_summary = np.sort(final_summary)
        positions = final_summary + 1 # index starts from 0 but it is better show from 1

        sentences = self.sentences['sentences'].iloc[final_summary]
        summary_indexes = np.array(np.unique(np.hstack(sentence_indexes[final_summary])), dtype=int)
        if len(summary_indexes) == 0:
            return sentences,positions,np.array([])
        _, nearest_neighbors = self.nearest_neighbors(self.distances, summary_indexes)
        get_word = lambda i: self.reversed_dictionary[self.reversed_distance_index_mapping[i]]
        nearest_words = np.vectorize(get_word)(nearest_neighbors)
        return sentences, positions, nearest_words

    def summarize(self, summary_length = 1000,return_words=False):
        lengths = self.sentences['sentences'].apply(len)
        if (lengths > summary_length).all():
            raise SummarySizeTooSmall("None of sentences is shorter than given length, cannot choose any sentences.")

        selected_sentences, positions, nearest_words = self.modified_greedy_algrorithm(summary_length)
        if return_words:
            return selected_sentences, positions, [self.dictionary[w] for w in self.words], \
                   [self.dictionary[nw] for nw in nearest_words]
        return selected_sentences, positions

    def calculate_distances(self, words):
        """
        Calculates euclidean distances between words.
        :param words:
        :return: distances and transformations for indexes
        """
        indexes = np.array([self.dictionary[w] for w in words])
        if len(indexes) == 0:
            return np.array([]), {}
        embeds = self.embeddings[indexes]
        distance_matrix = euclidean_distances(embeds,embeds)
        submatrix_indexes = dict(zip(indexes, np.arange(indexes.shape[0])))
        return distance_matrix, submatrix_indexes