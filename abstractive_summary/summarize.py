import pandas as pd
import numpy as np
import tensorflow as tf

import sys
import os
sys.path.append(os.path.abspath("../")) # not maybe the best way to structure but MVP
from tools.tools import load_data
txt_section_split_by = "\n[ ]*\n"
import re
import preprocessing as prep
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

batch_size = 16

texts = load_data('../judgments/test_data/')

embeddings = np.load('../embeddings/data/embeddings.npy')
dictionary = np.load('../embeddings/data/dictionary.npy').item()
# Special tokens that will be added to our vocab
codes = ["<UNK>","<PAD>","<EOS>","<GO>"]
# Add codes to vocab
for code in codes:
    dictionary[code] = len(dictionary)
reverse_dictionary = dict(zip(range(len(dictionary.keys())),dictionary.keys()))

pad_index = dictionary['<PAD>']

section_splitter = re.compile(txt_section_split_by)
parser = lambda text: [s.strip() for s in section_splitter.split(text) if len(s.strip()) > 2][-1]
texts['target'] = texts['text'].apply(parser)

text_len = 800
summary_len = 20
texts = prep.convert_texts_to_indexes(texts, dictionary, text_len, summary_len)

input_sentence, text = texts[['text', 'text_indexes']].iloc[0]

checkpoint = "./best_model.ckpt"

loaded_graph = tf.Graph()
with tf.Session(graph=loaded_graph) as sess:
    # Load saved model
    loader = tf.train.import_meta_graph(checkpoint + '.meta')
    loader.restore(sess, checkpoint)

    input_data = loaded_graph.get_tensor_by_name('input:0')
    logits = loaded_graph.get_tensor_by_name('predictions:0')
    text_length = loaded_graph.get_tensor_by_name('text_length:0')
    summary_length = loaded_graph.get_tensor_by_name('summary_length:0')
    keep_prob = loaded_graph.get_tensor_by_name('keep_prob:0')
    
    #Multiply by batch_size to match the model's input parameters
    answer_logits = sess.run(logits, {input_data: [text]*batch_size, 
                                      summary_length: [np.random.randint(15,18)],
                                      text_length: [len(text)]*batch_size,
                                      keep_prob: 1.0})[0] 

# Remove the padding from the tweet
pad = dictionary["<PAD>"]

print('Original Text:', input_sentence)

print('\nText')
#print('  Word Ids:    {}'.format([i for i in text]))
#print('  Input Words: {}'.format(" ".join([int_to_vocab[i] for i in text])))

print('\nSummary')
print('  Word Ids:       {}'.format([i for i in answer_logits if i != pad]))
print('  Response Words: {}'.format(" ".join([reverse_dictionary[i] for i in answer_logits if i != pad])))