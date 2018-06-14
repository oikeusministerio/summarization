
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import euclidean_distances


def plot_with_labels(low_dim_embs, labels, filename = None):
    assert low_dim_embs.shape[0] >= len(labels), 'More labels than embeddings'
    plt.figure(figsize=(18, 18))  # in inches
    for i, label in enumerate(labels):
        x, y = low_dim_embs[i, :]
        plt.scatter(x, y)
        plt.annotate(
            label,
            xy=(x, y),
            xytext=(5, 2),
            textcoords='offset points',
            ha='right',
            va='bottom')
    if filename == None:
        plt.show()
    else:
        plt.savefig(filename)

class EmbeddingsReader:

    def __init__(self, embed_file = "data/embeddings.npy", \
                 dico_file="data/dictionary.npy"):
        self.embeddings = np.load(embed_file)
        self.dictionary = np.load(dico_file).item()
        self.reversed_dictionary = dict(zip(self.dictionary.values(), self.dictionary.keys()))

    def visualize_embeddings(self, N, filename=None):
        tsne = TSNE(
            perplexity=30, n_components=2, init='pca', n_iter=5000, method='exact')
        plot_only = N
        low_dim_embs = tsne.fit_transform(self.embeddings[:plot_only, :])
        labels = [self.reversed_dictionary[i] for i in range(plot_only)]

        plot_with_labels(low_dim_embs, labels, filename)

    def similarity_word_to_word(self, word1, word2, metric="euclidean"):
        i1 = self.dictionary[word1]
        i2 = self.dictionary[word2]
        w1 = self.embeddings[i1].reshape(1,-1)
        w2 = self.embeddings[i2].reshape(1,-1)
        return euclidean_distances(w1,w2)

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
        return euclidean_distances(w, text_embeddings).min()