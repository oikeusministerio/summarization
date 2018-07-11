
from nltk import word_tokenize
import numpy as np
import re


def convert_texts_to_indexes(texts, dictionary, N_orig, N_target, take_all=False):
    """
    Texts should be pandas.DataFrame containing texts to handle.
    Dictionary is a dict that contains used vocabylary.
    """
    word_splitting = lambda t : [w for w in word_tokenize(t.strip().lower()) \
                                 if len(w) > 1 and re.match('[^0-9]', w) and w in dictionary]
    word_splitting_text = lambda t: word_splitting(t)[:N_orig]
    word_splitting_target = lambda t: word_splitting(t)[:N_target]
    if take_all:
        word_splitting_text = word_splitting
        word_splitting_target = word_splitting
    texts['text_words'] = texts['text'].apply(word_splitting_text)
    texts['target_words'] = texts['target'].apply(word_splitting_target)

    texts['text_lengths'] = texts['text_words'].apply(len)
    texts['target_lengths'] = texts['target_words'].apply(len)
    if not take_all:
        texts = texts[np.logical_and(texts.text_lengths > (N_orig // 3), texts.target_lengths > (N_target // 3))]
        texts = texts.reset_index(drop=True)

    texts = texts[np.logical_and(texts.text_lengths > 0, texts.target_lengths > 0)] # skip empty ones
    texts = texts.reset_index(drop=True)
    print("texts: " + str(texts.shape[0]))
    print("mean length " + str(texts.text_lengths.mean()))
    print("mean length " + str(texts.target_lengths.mean()))
    texts['text_indexes'] = texts['text_words'].apply(lambda word_list: np.vectorize(dictionary.get)(word_list))
    texts['target_indexes'] = texts['target_words'].apply(lambda word_list: np.vectorize(dictionary.get)(word_list))
    return texts[['text','target','text_indexes','target_indexes']]