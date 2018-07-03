
from nltk import sent_tokenize, word_tokenize
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter

def plot_with_labels(original_embs, summary_embs, top_words, top_word_embeddings,file_destination = None):
    plt.rcParams.update({'font.size': 22})
    fig = plt.figure(figsize=(18, 18))  # in inches
    ax = fig.add_subplot(111)
    fig.suptitle('Moniulotteiset sanavektorit visualisoituna \n PCA ja TSNE menetelmien avulla kaksiulotteisessa avaruudessa.')
    ax.scatter(original_embs[:,0], original_embs[:,1], color='r', label='Alkuperäisen tekstin sanat')
    ax.scatter(summary_embs[:, 0], summary_embs[:, 1], color='b', label='Lopullisen tiivistelmän sanat, jotka lähimpinä naapureina alkup. sanoille.')
    for i in range(len(top_words)):
        ax.annotate(top_words[i],
                    xy=top_word_embeddings[i,:],
                    xytext=(5, 2),
                    textcoords='offset points',
                    ha='right',
                    va='bottom');
    ax.legend(loc=2, prop={'size': 24})
    if file_destination == None:
        plt.show()
    else:
        fig.savefig(file_destination)

def find_top_words(nearest_neighbors, reverse_dictionary):
    n_words = np.min([len(nearest_neighbors), 10])
    counter = Counter(nearest_neighbors)
    top_word_indexes = [x[0] for x in counter.most_common(n_words)]
    top_words = [reverse_dictionary[i] for i in top_word_indexes]
    nearest_neighbors = np.array(nearest_neighbors)
    original_array_indexes = [np.where(nearest_neighbors == i)[0][0] for i in top_word_indexes] # first index is enough
    return top_words, original_array_indexes

def visualize_embedding_results(original_words_indexes, nearest_neighbors_indexes, reverse_dictionary, embeddings, file_destination=None):
    top_words, top_word_indexes = find_top_words(nearest_neighbors_indexes, reverse_dictionary)

    all_words_indexes = np.concatenate([original_words_indexes, nearest_neighbors_indexes])
    embeddings_to_plot = embeddings[all_words_indexes]

    pca = PCA(n_components=15)
    n_dimensional_embeddings = pca.fit_transform(embeddings_to_plot)

    tsne = TSNE(
        perplexity=25, n_components=2, init='pca', n_iter=400)


    two_dimensional_embeddings = tsne.fit_transform(n_dimensional_embeddings)

    two_dim_original_embs = two_dimensional_embeddings[:len(original_words_indexes)]
    two_dim_summary_embs = two_dimensional_embeddings[len(original_words_indexes):]
    plot_with_labels(two_dim_original_embs, two_dim_summary_embs, \
                     top_words, two_dim_summary_embs[top_word_indexes], file_destination=file_destination)