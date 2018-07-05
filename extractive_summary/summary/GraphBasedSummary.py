import numpy as np
import pandas as pd
import re


from tools.exceptions import SummarySizeTooSmall, TextTooLong
from tools.tools import sentence_tokenize

from nltk import word_tokenize
import gensim.summarization.summarizer as summarizer

class GraphBasedSummary:

    max_sentences = 250
    min_sentences = 3

    def __init__(self, text, threshold=0.1):
        self.sentences = self.split_sentences(text)
        N = len(self.sentences)
        if N > GraphBasedSummary.max_sentences:
            raise TextTooLong(" " +  str(N) + " sentences are too many for the graph based method (max "+GraphBasedSummary.max_sentences+").")
        self.dumping_factor = 0.85
        self.threshold = threshold
        summarizer.INPUT_MIN_LENGTH = GraphBasedSummary.min_sentences

    def split_sentences(self, text):
        clean_one_chars = r"[ ][A-Za-z]\.[ ]"
        text = re.sub(clean_one_chars, ' ', text)

        sentences = sentence_tokenize(text)
        sentences = [s for s in sentences if len(s) > 2]
        lengths = [len(word_tokenize(s)) for s in sentences]
        # add id to give order for sentences later
        data = pd.DataFrame({'position': np.arange(len(sentences)),
                             'sentence': np.array(sentences),
                             'lengths': lengths})
        data['sentence'] = data['sentence'].astype(str)
        return data

    def get_positions(self, sentences):
        original_sents = self.sentences['sentence'].values
        positions = []
        for sent in sentences:
            indexes = np.where(original_sents == sent)[0]
            if len(indexes) > 0:
                pos = indexes[0]
                original_sents[pos] += str(pos) # mark this way that is is allready used
            else:
                pos = -1
            positions.append(pos)
        return np.array(positions)

    def summarize(self, word_count=50):
        """
        :param summary_length: number of words to use in summary
        :return: summary
        """
        # ensure that we can choose any of the sentences
        word_count = np.max([word_count, self.sentences['lengths'].max()])
        text = "\n".join(self.sentences['sentence'])
        if self.sentences.shape[0] < 3: # no sense of summarizing such a short text
            return " ".join(self.sentences['sentence']),np.arange(3)
        selected_sentences = summarizer.summarize(text, word_count=word_count, split=True)
        if len(selected_sentences) == 0:
            return [],[]
        return selected_sentences, self.get_positions(selected_sentences)