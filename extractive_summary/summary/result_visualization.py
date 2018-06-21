
from nltk import sent_tokenize, word_tokenize
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def plot_with_labels(original_embs, summary_embs, filename = None):
    plt.figure(figsize=(18, 18))  # in inches
    plt.scatter(original_embs[:,0], original_embs[:,1], color='r', label='Original')
    plt.scatter(summary_embs[:, 0], summary_embs[:, 1], color='b', label='Summary')
    plt.legend()
    if filename == None:
        plt.show()
    else:
        plt.savefig(filename)

def visualize_embedding_results(original_words, summary_sentences, dictionary, embeddings_file):
    original_words_indexes = [dictionary[w] for w in original_words]

    summary_words = np.hstack([word_tokenize(sentence, language="finnish") for sentence in summary_sentences])
    summary_words = np.array([w.lower() for w in summary_words if w.lower() in dictionary])  # ATTENTION! Skipping unknown words here.
    summary_words = np.unique(summary_words)
    summary_words = np.array([w for w in summary_words if len(w) > 1])

    summary_word_indexes = [dictionary[w] for w in summary_words]

    # let's take only those original words that are not selected in summary
    original_words_indexes = [i for i in original_words_indexes if i not in summary_word_indexes]

    embeddings = np.load(embeddings_file)
    all_words_indexes = np.concatenate([original_words_indexes, summary_word_indexes])
    #original_embeddings = embeddings[original_words_indexes]
    embeddings_to_plot = embeddings[all_words_indexes]

    pca = PCA(n_components=15)
    three_dimensional_embeddings = pca.fit_transform(embeddings_to_plot)

    tsne = TSNE(
        perplexity=25, n_components=2, init='pca', n_iter=400)


    two_dimensional_embeddings = tsne.fit_transform(three_dimensional_embeddings)

    two_dim_original_embs = two_dimensional_embeddings[:len(original_words_indexes)]
    two_dim_summary_embs = two_dimensional_embeddings[len(original_words_indexes):]
    plot_with_labels(two_dim_original_embs, two_dim_summary_embs, filename='result.png')