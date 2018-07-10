
import tensorflow as tf
import math
from nltk import word_tokenize
import re
import numpy as np
import collections
import random
from summarization.tools.tools import load_data, word_is_valid

only_alphabet_regex = '^[^\W\d_]+$'

def build_dataset(words, n_words):
    """Process raw inputs into a dataset."""
    words = [w for w in words if word_is_valid(w)]
    count = [['UNK', -1]]
    count.extend(collections.Counter(words).most_common(n_words - 1))
    dictionary = dict()
    only_alphabet = re.compile(only_alphabet_regex)
    for word, _ in count:
        #if only_alphabet.match(word):
        dictionary[word] = len(dictionary)
    data = list()
    unk_count = 0
    for word in words:
        index = dictionary.get(word, 0)
        if index == 0:  # dictionary['UNK']
            unk_count += 1
        data.append(index)
    count[0][1] = unk_count
    reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
    return(data, count, dictionary, reversed_dictionary)

#learn
# Function to generate a training batch for the skip-gram model.
def generate_batch(data, data_index, batch_size, num_skips, skip_window):
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    span = 2 * skip_window + 1  # [ skip_window target skip_window ]
    buffer = collections.deque(maxlen=span)  # pylint: disable=redefined-builtin
    if data_index + span > len(data):
        data_index = 0
    buffer.extend(data[data_index:data_index + span])
    data_index += span
    for i in range(batch_size // num_skips):
        context_words = [w for w in range(span) if w != skip_window]
        words_to_use = random.sample(context_words, num_skips)
        for j, context_word in enumerate(words_to_use):
            batch[i * num_skips + j] = buffer[skip_window]
            labels[i * num_skips + j, 0] = buffer[context_word]
        if data_index == len(data):
            buffer.extend(data[0:span])
            data_index = span
        else:
            buffer.append(data[data_index])
            data_index += 1
    # Backtrack a little bit to avoid skipping words in the end of a batch
    data_index = (data_index + len(data) - span) % len(data)
    return data_index, batch, labels

class EmbeddingLearner:

    def __init__(self, source_dir, destination_dir, settings):
        """

        :param source_dir: where to find data files
        :param destination_dir: where to save output
        :param settings: learning params
        """
        self.source_dir = source_dir # "../judgements/data"
        self.destination_dir = destination_dir
        self.batch_size = settings['batch_size']
        self.embedding_size = settings['embedding_size']
        self.skip_window = settings['skip_window']
        self.num_skips = settings['num_skips']
        self.num_sampled = settings['num_sampled']
        self.num_steps = settings['num_steps']
        self.vocabulary_size = settings['vocabulary_size']

    # # learning params
    # batch_size = 128
    # embedding_size = 128  # Dimension of the embedding vector.
    # skip_window = 2  # How many words to consider left and right.
    # num_skips = 4  # How many times to reuse an input to generate a label.
    # num_sampled = 64 # Number of negative examples to sample.
    # num_steps = 100001
    # vocabulary_size = 50000  # words to consider

    def run(self):
        print("read data from : ", self.source_dir)
        texts = load_data(self.source_dir)

        all_texts = " ".join(texts['text'].values).lower()
        words = word_tokenize(all_texts, language="finnish")
        print("read words: " + str(len(words)))

        data, count, dictionary, reverse_dictionary = build_dataset(words, self.vocabulary_size)

        graph = tf.Graph()
        with graph.as_default():
            # Placeholders for inputs
            with tf.name_scope('inputs'):
                train_inputs = tf.placeholder(tf.int32, shape=[self.batch_size])
                train_labels = tf.placeholder(tf.int32, shape=[self.batch_size, 1])

            with tf.device('/gpu:0'):
                # Look up embeddings for inputs.
                with tf.name_scope('embeddings'):
                    embeddings = tf.Variable(tf.random_uniform([self.vocabulary_size, self.embedding_size], -1.0, 1.0))
                    embed = tf.nn.embedding_lookup(embeddings, train_inputs)

                with tf.name_scope('weights'):
                    nce_weights = tf.Variable(
                        tf.truncated_normal(
                            [self.vocabulary_size, self.embedding_size],
                            stddev=1.0 / math.sqrt(self.embedding_size)))
                with tf.name_scope('biases'):
                    nce_biases = tf.Variable(tf.zeros([self.vocabulary_size]))

            with tf.name_scope('loss'):
                # Compute the NCE loss, using a sample of the negative labels each time.
                loss = tf.reduce_mean(tf.nn.nce_loss(weights=nce_weights, \
                                 biases=nce_biases, \
                                 labels=train_labels, \
                                 inputs=embed, \
                                 num_sampled=self.num_sampled,\
                                 num_classes=self.vocabulary_size))

            with tf.name_scope('optimizer'):
                optimizer = tf.train.GradientDescentOptimizer(learning_rate=1.0).minimize(loss)

            # Compute the cosine similarity between minibatch examples and all embeddings.
            norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
            normalized_embeddings = embeddings / norm

            # Add variable initializer.
            init = tf.global_variables_initializer()

        with tf.Session(graph=graph) as session:

            init.run()
            data_index = 0
            for step in range(self.num_steps):
                data_index, batch_inputs, batch_labels = generate_batch(data, data_index, self.batch_size, self.num_skips,
                                                            self.skip_window)
                feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}
                _, cur_loss = session.run([optimizer, loss], feed_dict=feed_dict)
                if step % 500 == 0:
                    print(cur_loss)
            final_embeddings = normalized_embeddings.eval()


        print("Finished, save to file")
        embed_filename = self.destination_dir + "embeddings.npy"
        dico_filename = self.destination_dir + "dictionary.npy"
        np.save(embed_filename, final_embeddings)
        np.save(dico_filename, dictionary)

        return embed_filename, dico_filename