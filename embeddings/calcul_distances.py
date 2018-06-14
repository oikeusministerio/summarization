
import tensorflow as tf
import numpy as np

embed_file="data/embeddings.npy"
embeddings_values = np.load(embed_file)

embeddings_N = embeddings_values.shape[0]
embeddings_dim = embeddings_values.shape[1]

#import pdb; pdb.set_trace()

graph = tf.Graph()

with graph.as_default():
    # Placeholders for inputs
    with tf.name_scope('inputs'):
        embeddings = tf.placeholder(tf.float32, shape=[embeddings_N,embeddings_dim])

    with tf.device('/gpu:0'):
        similarity = tf.matmul(embeddings, embeddings, transpose_b=True)

    # Add variable initializer.
    init = tf.global_variables_initializer()


with tf.Session(graph=graph) as session:

    init.run()

    feed_dict = {embeddings: embeddings_values}
    sim = session.run(similarity, feed_dict=feed_dict)

    print(sim.shape)
    #top_k = 8  # number of nearest neighbors
    #nearest = (-sim[i, :]).argsort()[1:top_k + 1]
    #log_str = 'Nearest to %s:' % valid_word
