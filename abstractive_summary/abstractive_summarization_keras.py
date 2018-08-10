

import pandas as pd
import numpy as np
import tensorflow as tf
import time
from nltk import word_tokenize


import sys
import os
sys.path.append(os.path.abspath("../")) # not maybe the best way to structure but MVP
from summarization.tools.tools import load_data
txt_section_split_by = "\n[ ]*\n"
import re
import preprocessing as prep
from keras.preprocessing.sequence import pad_sequences
import argparse
from collections import Counter

parser = argparse.ArgumentParser(description="Learn model for abstractive summarization.")
optional = parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
required.add_argument('-source_dir', help='Path to raw text files used for learning', required=True)
required.add_argument('-texts_length',
                      help='Fixed size of source texts. Texts that have less words than texts_length are padded with empty words. ' + \
                      'If there are more words in text than texts_length, those extra words are discarded. -1 takes every word from texts and targets.',
                      required=True, type=int)
required.add_argument('-target_length', help='Similar with texts_length but applies to targets. -1 takes every word from texts and targets.',
                      required=True, type=int)
required.add_argument('-dictionary_length', help='Number of words to take in account in dictionary.', required=True, type=int)
required.add_argument('-epochs', nargs='?', const=10, type=int, default=10)
args = parser.parse_args()

texts = load_data(args.source_dir) #'judgments/data/'

counter = Counter()
for item in texts.iterrows():
    text = item[1]['text']
    words = word_tokenize(text)
    counter.update(words)

dictionary = dict(zip(np.array(counter.most_common(args.dictionary_length))[:,0], np.arange(args.dictionary_length)))

codes = ["<UNK>","<PAD>","<EOS>","<GO>"]
for code in codes:
    dictionary[code] = len(dictionary)
reverse_dictionary = dict(zip(range(len(dictionary.keys())),dictionary.keys()))

print("Dictionary length : " + str(len(dictionary.keys())))

pad_index = dictionary['<PAD>']

section_splitter = re.compile(txt_section_split_by)
parser = lambda text: [s.strip() for s in section_splitter.split(text) if len(s.strip()) > 2][-1]
texts['target'] = texts['text'].apply(parser)

take_all = args.texts_length == -1 or args.target_length == -1
texts = prep.convert_texts_to_indexes(texts, dictionary, args.texts_length, args.target_length, take_all=take_all)
X = pad_sequences(texts.text_indexes, padding='post', value=pad_index)
Y = pad_sequences(texts.target_indexes, padding='post', value=pad_index)

