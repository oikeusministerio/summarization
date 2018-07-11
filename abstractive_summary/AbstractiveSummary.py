import pandas as pd
import numpy as np
import tensorflow as tf

class AbstractiveSummary:

    def __init__(self, dictionary):
        self.batch_size = 16
        self.checkpoint = "./abstractive_summary/best_model.ckpt"
        self.dictionary = dictionary
        self.reverse_dictionary = dict(zip(range(len(dictionary.keys())),dictionary.keys()))

    def summarize(self, text, input_sequence, length):
        loaded_graph = tf.Graph()
        with tf.Session(graph=loaded_graph) as sess:
            # Load saved model
            loader = tf.train.import_meta_graph(self.checkpoint + '.meta')
            loader.restore(sess, self.checkpoint)

            input_data = loaded_graph.get_tensor_by_name('input:0')
            logits = loaded_graph.get_tensor_by_name('predictions:0')
            text_length = loaded_graph.get_tensor_by_name('text_length:0')
            summary_length = loaded_graph.get_tensor_by_name('summary_length:0')
            keep_prob = loaded_graph.get_tensor_by_name('keep_prob:0')

            #Multiply by batch_size to match the model's input parameters
            answer_logits = sess.run(logits, {input_data: [input_sequence]*self.batch_size,
                                              summary_length: [np.random.randint(length,length + 3)],
                                              text_length: [len(input_sequence)]*self.batch_size,
                                              keep_prob: 1.0})[0]

        # Remove the padding from the tweet
        pad = self.dictionary["<PAD>"]

        print('Original Text:', text)

        print('\nSummary')
        print('  Word Ids:       {}'.format([i for i in answer_logits if i != pad]))
        print('  Response Words: {}'.format(" ".join([self.reverse_dictionary[i] for i in answer_logits if i != pad])))