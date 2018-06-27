
# coding: utf-8

import pandas as pd
import json
import numpy as np
import redis
import pickle
from sklearn.metrics.pairwise import euclidean_distances, cosine_distances


judgement_scores = pd.read_csv('FinnSim_judgment_scores.csv', sep=';')
judgement_scores['sim_score'] = pd.to_numeric(judgement_scores['sim_score'],errors='coerce')
judgement_scores = judgement_scores.dropna()


dir_path = '../../'
with open(dir_path + 'extractive_summary/config.json', 'r') as f:
    config = json.load(f)
dictionary = np.load(dir_path + config['dictionary_file']).item()
embeddings = np.load(dir_path + config['embeddings_file'])


reference_words = np.hstack(judgement_scores[['word1','word2']].values)
words_present = np.array([1 for rf in reference_words if rf in dictionary]).sum()
print("words present "+ str(words_present / len(reference_words)))



word_pairs_present = judgement_scores[['word1','word2']].apply(lambda x: x[0] in dictionary and x[1] in dictionary, axis=1)
print("words pairs present: " + str(word_pairs_present.sum() / judgement_scores.shape[0]))



#conn = redis.Redis(config["redis_address"],port=config["redis_port"])
#find_distance = lambda x: np.array(pickle.loads(conn.get(dictionary[x[0]])))[0][dictionary[x[1]]]
def get_embed(x):
    return embeddings[dictionary[x]].reshape(1,-1)

find_eulidean_distance = lambda x: euclidean_distances(get_embed(x[0]),get_embed(x[1]))[0][0]
find_cosine_distance = lambda x: cosine_distances(get_embed(x[0]),get_embed(x[1]))[0][0]

judgement_scores['eulidean_distance'] = judgement_scores[['word1','word2']][word_pairs_present].apply(find_eulidean_distance, axis=1)
judgement_scores['cosine_distance'] = judgement_scores[['word1','word2']][word_pairs_present].apply(find_cosine_distance, axis=1)



# In[124]:


scores = judgement_scores[word_pairs_present]
print("correlation between sim_score and euclidean distance: " + str(np.corrcoef(scores['eulidean_distance'],scores['sim_score'])))
print("correlation between sim_score and cosine distance: " + str(np.corrcoef(scores['cosine_distance'],scores['sim_score'])))

