
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

class EmbeddingsReader:

    def __init__(self, embed_file = "../../embeddings/data/embeddings.npy", \
                 dico_file="../../embeddings/data/dictionary.npy"):
        if embed_file is not None and dico_file is not None:
            self.embeddings = np.load(embed_file)
            self.dictionary = np.load(dico_file).item()
            self.reversed_dictionary = dict(zip(self.dictionary.values(), self.dictionary.keys()))

    def similarity_word_to_word(self, word1, word2, metric="euclidean"):
        i1 = self.dictionary[word1]
        i2 = self.dictionary[word2]
        w1 = self.embeddings[i1].reshape(1,-1)
        w2 = self.embeddings[i2].reshape(1,-1)
        return euclidean_distances(w1,w2)[0][0]

    def similarity_word_to_text(self, word, text, metric="euclidean"):
        """

        Kobayashi, Hayato, Masaki Noguchi, and Taichi Yatsuka.
        "Summarization based on embedding distributions."
        Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing. 2015.

        3th page, chapter
        Similarity Based on Embedding Distributions

        :param word: word
        :param text: text as list of words
        :param metric:
        :return:
        """
        i = self.dictionary[word]
        w = self.embeddings[i].reshape(1, -1)
        text_embeddings = [self.embeddings[self.dictionary[wi]] for wi in text if wi in self.dictionary]
        dist = euclidean_distances(w, text_embeddings)
        return dist.min()