
import redis
import pickle
import numpy as np
import pandas as pd
from nltk import sent_tokenize, word_tokenize
from sklearn.metrics.pairwise import euclidean_distances
import json
from .result_visualization import visualize_embedding_results
import time

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
        self.r = 0.5  # scaling factor, must be positive
        # when searching argmax, indexes with this value are not selected
        # becouse it is so big
        self.max_distance = -10000000
        with open('extractive_summary/config.json', 'r') as f:
            config = json.load(f)
            self.redis_address = config["redis_address"]
            self.redis_port = config["redis_port"]
            self.embeddings_file = config["embeddings_file"]
            self.embeddings = np.load(self.embeddings_file)
            self.get_redis_client = redis_client_constructor if redis_client_constructor != None else self.redis_client
            tic = time.time()
            #self.distances, self.distance_index_mapping = self.calculate_distances(self.words)
            self.distances, self.distance_index_mapping = self.fetch_distances_old(self.words)
            self.reversed_distance_index_mapping = dict(zip(self.distance_index_mapping.values(), \
                                                            self.distance_index_mapping.keys()))
            toc = time.time()
            print("calculating distances took " + str(1000 * (toc - tic)))

    def split_document(self, text, minimum_sentence_length=5):
        sentences = sent_tokenize(text, language="finnish")
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
        index_mapping = {i:candidate_summary_indexes[i] for i in range(len(candidate_summary_indexes))}
        candidate_document_distances = distances[:, candidate_summary_indexes]
        # before selecting minimun distances, let's avoid selecting, that the nearest one is the point himself
        cand_sums = candidate_document_distances[candidate_summary_indexes]
        np.fill_diagonal(cand_sums, 1000)  # let's put big value so that diagonal will not be chosen
        candidate_document_distances[candidate_summary_indexes] = cand_sums
        nearests = candidate_document_distances.argmin(axis=1)
        distances = candidate_document_distances.min(axis=1)
        return distances,np.array([index_mapping[i] for i in nearests])

    def get_candidate_summary_indexes(self, candidate_summary):
        return np.array([self.distance_index_mapping[self.dictionary[w.lower()]] \
                         for w in candidate_summary if w.lower() in self.dictionary])

    def nearest_neighbor_objective_function(self, candidate_summary):
        """
        Counts the distance between candidate_summary and document (words of original document).

        :param candidate_summary: list of words => current summary in iterative optimisation process
        :return: negative distance between candidate and sentences
        """
        candidate_summary_indexes = self.get_candidate_summary_indexes(candidate_summary)

        if len(candidate_summary_indexes) == 0: # this shouldn't hopefully happen, that we have sentence without any word in dictionary. But just in case
            return self.max_distance # let's not choose sentences that contains no known words

        nearests_document_word_distances, _ = self.nearest_neighbors(self.distances, candidate_summary_indexes)
        return -nearests_document_word_distances.sum()

    def get_positions(self, candidate_summary):
        positions = []
        for chosen in candidate_summary:
            for i, s in enumerate(self.sentences["sentences"]):
                if s == chosen:
                    positions.append(i)
                    break;
        df = pd.DataFrame({"sentences":np.array(candidate_summary), "positions":np.array(positions)})
        df = df.sort_values(by = "positions")
        return df["sentences"].values, df["positions"].values

    def split_sentences(self,sentences):
        """
        :param sentences: array of sentences
        :return: array of words
        """
        assert len(sentences) > 0, "Provide at least one sentence."
        return np.hstack([np.array(word_tokenize(s, language="finnish")) for s in sentences])

    def precalcule_sentence_distances(self, sentences_left):
        sentence_distances = np.array([self.nearest_neighbor_objective_function(self.split_sentences(np.array([s]))) for s in sentences_left])
        sentence_length = np.array([len(s) for s in sentences_left])
        return sentence_distances, sentence_length

    def modified_greedy_algrorithm(self, summary_size):
        """

        Implementation of Algorithm 1 in chapter 3

        :param summary_size: the size of summary to be made
        :return: summary
        """
        #sentences_left = self.sentences['sentences'].values # U in algorithm
        #sentences_left = np.array(self.sentences.index.tolist())  # U in algorithm
        print("precalcule")
        sentence_distances, sentence_lengths = self.precalcule_sentence_distances(self.sentences['sentences'].values)
        candidate_summary = np.array([]) # C in algorithm
        handled = np.array([], dtype=int)  # (C \ handled) in algorithm, in other words : list of indexes not in C (C is thing of algiruthm)
        candidate_distances_sum = 0
        candidate_char_count = 0
        print("iterate")
        while(handled.shape[0] < sentence_distances.shape[0]):
            s_candidates = (sentence_distances + candidate_distances_sum) / (sentence_lengths ** self.r)
            distance_min_border = s_candidates.min() - 1000 # indexes with this value cannot be maximum
            if handled.shape[0] > 0:
                s_candidates[handled] = distance_min_border # this way we dont choose same twice
            s_star_i = s_candidates.argmax()

            if candidate_char_count + sentence_lengths[s_star_i]  <= summary_size:
                candidate_summary = np.append(candidate_summary, s_star_i)
                candidate_char_count += sentence_lengths[s_star_i]
                candidate_distances_sum += sentence_distances[s_star_i]

            handled = np.append(handled, s_star_i)

        # then let's consider sentence, that is the best all alone, algorithm line 6
        sentences_left = self.sentences['sentences'].values
        s_candidates = np.array([
            self.nearest_neighbor_objective_function(self.split_sentences(np.array([s]))) \
            if len(s) <= summary_size else self.max_distance
            for s in sentences_left])
        s_star = sentences_left[s_candidates.argmax()]

        if len(candidate_summary) == 0: # summary_size smaller than any of sentences
            return np.array([]),np.array([]), np.array([])

        # and now choose eiher the best sentence or combination, algorithm line 7
        if s_candidates.max() > self.nearest_neighbor_objective_function(self.split_sentences(candidate_summary)):
            final_summary = np.array([s_star])
        else:
            final_summary = candidate_summary

        sentences, positions = self.get_positions(final_summary)
        summary_indexes = self.get_candidate_summary_indexes(self.split_sentences(final_summary))
        if len(summary_indexes) == 0:
            return sentences,positions,np.array([])
        _, nearest_neighbors = self.nearest_neighbors(self.distances, summary_indexes)
        nearest_words = np.array([self.reversed_dictionary[self.reversed_distance_index_mapping[i]] \
                                  for i in nearest_neighbors])

        return sentences, positions, nearest_words

    def summarize(self, summary_length = 1000,return_words=False):
        selected_sentences, positions, nearest_words = self.modified_greedy_algrorithm(summary_length)
        if return_words:
            return selected_sentences, positions, [self.dictionary[w] for w in self.words], \
                   [self.dictionary[nw] for nw in nearest_words]
        return selected_sentences, positions

    def redis_client(self):
        return redis.Redis(self.redis_address, port=self.redis_port)

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

    def fetch_distances_old(self, words):
        """
        Connects to redis database, that contains distances between all words, and fetches only words needed.
        Vocabulary of each individuel text is supposed to contain so few words that they fit to memory.
        :param words:
        :return: distances and transformations for indexes
        """
        connection = self.get_redis_client()
        indexes = np.array([self.dictionary[w] for w in words])

        N = len(indexes)
        distance_matrix = np.zeros((N,N))

        submatrix_indexes = {}
        for i,ind in enumerate(indexes):
            submatrix_indexes[ind] = i
            b_word_distances = connection.get(ind)
            word_distances = np.array(pickle.loads(b_word_distances))

            distance_matrix[i] = word_distances[0, indexes] # distance vector vector size of (1,vocab_size)

        return distance_matrix, submatrix_indexes