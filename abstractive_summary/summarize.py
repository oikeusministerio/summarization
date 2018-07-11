
import numpy as np
import sys
import os
sys.path.append(os.path.abspath("../")) # not maybe the best way to structure but MVP
from summarization.tools.tools import load_data
txt_section_split_by = "\n[ ]*\n"
import re
import preprocessing as prep
from AbstractiveSummary import AbstractiveSummary
import argparse

parser = argparse.ArgumentParser(description="Summarize one text with abstractive model.")
optional = parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
required.add_argument('-source_dir', help='Path to raw text files used for learning', required=True)
required.add_argument('-embeddings_dir', help='Path to folder that contains embeddings and dictionary.', required=True)
required.add_argument('-index', help='The index of targeted text in dataset.', nargs='?', const=0, type=int, default=0)
required.add_argument('-summary_length', help='The length of produced summary in words. Default 5.', nargs='?', const=5, type=int, default=5)
args = parser.parse_args()

texts = load_data(args.source_dir) #'judgments/test_data/'

embeddings = np.load(args.embeddings_dir + 'embeddings.npy') # embeddings/data/
dictionary = np.load(args.embeddings_dir + 'dictionary.npy').item()

# Special tokens that will be added to our vocab
codes = ["<UNK>","<PAD>","<EOS>","<GO>"]
# Add codes to vocab
for code in codes:
    dictionary[code] = len(dictionary)
reverse_dictionary = dict(zip(range(len(dictionary.keys())),dictionary.keys()))

pad_index = dictionary['<PAD>']

#section_splitter = re.compile(txt_section_split_by)
#parser = lambda text: [s.strip() for s in section_splitter.split(text) if len(s.strip()) > 2][-1]
texts['target'] = "Sivuutetaan tämä parsiminen. " #texts['text'].apply(parser)

text_len = -1
summary_len = -1
texts = prep.convert_texts_to_indexes(texts, dictionary, text_len, summary_len, take_all=False)

text,input_sentence = texts[['text', 'text_indexes']].iloc[args.index]

summary = AbstractiveSummary(dictionary)
summary.summarize(text, input_sentence, args.summary_length)