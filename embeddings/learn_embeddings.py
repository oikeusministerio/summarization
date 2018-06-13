
import os
import tensorflow as tf
from sklearn.feature_extraction.text import CountVectorizer
import math

from tools import load_data
import numpy as np
import collections
import random

fname = "../judgements/data"
print("read data from : ", fname)
texts = load_data('../judgements/data', N=10)

# count vocabulary
'''
vectorizer = CountVectorizer()
vectorizer.fit_transform(texts['text'])
vocabulary = vectorizer.vocabulary_

vocabulary_size = len(vocabulary)
word2index = vocabulary
index2word = {}
for w, i in word2index.items():
    index2word[i] = w
'''

vocabulary_size = 50000

words = " ".join(texts['text'].values)

def build_dataset(words, n_words):
    """Process raw inputs into a dataset."""
    count = [['UNK', -1]]
    count.extend(collections.Counter(words).most_common(n_words - 1))
    dictionary = dict()
    for word, _ in count:
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

data, count, dictionary, reverse_dictionary = build_dataset(words, vocabulary_size)


# tensorflow
batch_size = 32
embedding_size = 32  # Dimension of the embedding vector.
skip_window = 1  # How many words to consider left and right.
num_skips = 2  # How many times to reuse an input to generate a label.
num_sampled = 16 # Number of negative examples to sample.

#learn
data_index = 0
# Step 3: Function to generate a training batch for the skip-gram model.
def generate_batch(batch_size, num_skips, skip_window):
    global data_index
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
    return batch, labels

graph = tf.Graph()

with graph.as_default():
    # Placeholders for inputs
    with tf.name_scope('inputs'):
        train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
        train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])

    with tf.device('/gpu:0'):
        # Look up embeddings for inputs.
        with tf.name_scope('embeddings'):
            embeddings = tf.Variable(tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
            embed = tf.nn.embedding_lookup(embeddings, train_inputs)

        with tf.name_scope('weights'):
            nce_weights = tf.Variable(
                tf.truncated_normal(
                    [vocabulary_size, embedding_size],
                    stddev=1.0 / math.sqrt(embedding_size)))
        with tf.name_scope('biases'):
            nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

    with tf.name_scope('loss'):
        # Compute the NCE loss, using a sample of the negative labels each time.
        loss = tf.reduce_mean(tf.nn.nce_loss(weights=nce_weights, \
                         biases=nce_biases, \
                         labels=train_labels, \
                         inputs=embed, \
                         num_sampled=num_sampled,\
                         num_classes=vocabulary_size))

    with tf.name_scope('optimizer'):
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=1.0).minimize(loss)

    # Compute the cosine similarity between minibatch examples and all embeddings.
    norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
    normalized_embeddings = embeddings / norm
    # Add variable initializer.
    init = tf.global_variables_initializer()

with tf.Session(graph=graph) as session:
    num_steps = 50000

    init.run()

    for step in range(num_steps):
        batch_inputs, batch_labels = generate_batch(batch_size, num_skips,
                                                        skip_window)
        feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}
        _, cur_loss = session.run([optimizer, loss], feed_dict=feed_dict)
        if step % 500 == 0:
            print(cur_loss)
    final_embeddings = normalized_embeddings.eval()


print("Finished, save to file")
np.savez("embeddings", final_embeddings)