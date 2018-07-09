
from nltk import word_tokenize
import numpy as np
import re


def convert_texts_to_indexes(texts, dictionary, N):
    """
    Texts should be pandas.DataFrame containing texts to handle.
    Dictionary is a dict that contains used vocabylary.
    """
    word_splitting = lambda t : [w for w in word_tokenize(t.strip().lower()) \
                                 if len(w) > 1 and re.match('[^0-9]', w) and w in dictionary][:N]
    texts['words'] = texts['text'].apply(word_splitting)
    texts['lengths'] = texts['words'].apply(len)
    print("mean length " + str(texts.lengths.mean()))
    texts['indexes'] = texts['words'].apply(lambda word_list: np.vectorize(dictionary.get)(word_list))
    return texts