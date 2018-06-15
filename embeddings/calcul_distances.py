
import redis
import numpy as np
import pickle
from sklearn.metrics.pairwise import euclidean_distances

embed_file="data/embeddings.npy"
embeddings = np.load(embed_file)

#import pdb; pdb.set_trace()

connection = redis.Redis('localhost')

for w1 in range(len(embeddings)):
    if w1 % 100 == 0:
        print(w1)

    distances = euclidean_distances(embeddings[w1, :].reshape(1, -1), embeddings)
    distances[0, w1] = 0 # diagonal is zero

    p_dist = pickle.dumps(distances)
    connection.set(w1, p_dist)
