
from nltk import sent_tokenize, word_tokenize
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def plot_with_labels(original_embs, summary_embs, file_destination = None):
    fig = plt.figure(figsize=(18, 18))  # in inches
    ax = fig.add_subplot(111)
    ax.scatter(original_embs[:,0], original_embs[:,1], color='r', label='Alkuperäisen tekstin sanat')
    ax.scatter(summary_embs[:, 0], summary_embs[:, 1], color='b', label='Lopullisen tiivistelmän sanojen lähimmät naapurit')
    ax.legend(loc=2, prop={'size': 32})
    if file_destination == None:
        plt.show()
    else:
        fig.savefig(file_destination)

def visualize_embedding_results(original_words_indexes, nearest_neighbors_indexes, dictionary, embeddings, file_destination=None):
    #original_words_indexes = [dictionary[w] for w in original_words]

    #nearest_neighbors_indexes = [dictionary[w] for w in nearest_neighbors]

    # let's take only those original words that are not selected in summary
    #original_words_indexes = [i for i in original_words_indexes if i not in summary_word_indexes]

    #embeddings = np.load(embeddings_file)
    all_words_indexes = np.concatenate([original_words_indexes, nearest_neighbors_indexes])
    #original_embeddings = embeddings[original_words_indexes]
    embeddings_to_plot = embeddings[all_words_indexes]

    pca = PCA(n_components=15)
    three_dimensional_embeddings = pca.fit_transform(embeddings_to_plot)

    tsne = TSNE(
        perplexity=25, n_components=2, init='pca', n_iter=400)


    two_dimensional_embeddings = tsne.fit_transform(three_dimensional_embeddings)

    two_dim_original_embs = two_dimensional_embeddings[:len(original_words_indexes)]
    two_dim_summary_embs = two_dimensional_embeddings[len(original_words_indexes):]
    plot_with_labels(two_dim_original_embs, two_dim_summary_embs, file_destination=file_destination)