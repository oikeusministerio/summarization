
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


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
