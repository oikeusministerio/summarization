
import os
import sys
sys.path.append(os.path.abspath("../")) # not maybe the best way to structure but MVP
from embeddings.EmbeddingLearner import EmbeddingLearner
from embeddings.evaluation.Evaluator import Evaluator

"""
self.source_dir = source_dir # "../judgements/data"
self.destination_dir = destination_dir
self.batch_size = settings['batch_size']
self.embedding_size = settings['embedding_size']
self.skip_window = settings['skip_window']
self.num_skips = settings['num_skips']
self.num_sampled = settings['num_sampled']
self.num_steps = settings['num_steps']
vocabulary_size = 50000 # words to consider
# directory, where to save embeddings 0and dictionary
data_dir =  sys.argv[2] # "data/"

# # learning params
# batch_size = 128
# embedding_size = 128  # Dimension of the embedding vector.
# skip_window = 2  # How many words to consider left and right.
# num_skips = 4  # How many times to reuse an input to generate a label.
# num_sampled = 64 # Number of negative examples to sample.
# num_steps = 100001

"""

params1 = {"batch_size":128,
          "embedding_size":64,
          "skip_window": 1,
          "num_skips": 2,
          "num_sampled":64,
          "num_steps": 100001,
          "vocabulary_size": 80000}

params2 = {"batch_size":128,
          "embedding_size":128,
          "skip_window": 2,
          "num_skips": 2,
          "num_sampled":64,
          "num_steps": 100001,
          "vocabulary_size": 80000}

params3 = {"batch_size":128,
          "embedding_size":128,
          "skip_window": 2,
          "num_skips": 4,
          "num_sampled":64,
          "num_steps": 100001,
          "vocabulary_size": 80000}

params4 = {"batch_size":128,
          "embedding_size":128,
          "skip_window": 1,
          "num_skips": 2,
          "num_sampled":64,
          "num_steps": 100001,
          "vocabulary_size": 80000}

params = [params1, params2, params3, params4]

def learn_embeddings(p):
    source_dir = "../judgements/data"
    destination_dir = "data/"
    learner = EmbeddingLearner(source_dir, destination_dir, p)
    return learner.run()

def evaluate(embed,dico):
    evaluator = Evaluator(embed, dico, "evaluation/FinnSim_judgment_scores.csv")
    res = evaluator.evaluate()
    euc = res[0][0][1]
    cos = res[0][1][0]
    return euc,cos

def iterate_all_params(params):
    results = []
    for i,p in enumerate(params):
        print(i)
        embed_filename, dico_filename = learn_embeddings(p)

        results.append(evaluate(embed_filename, dico_filename))
        print(results)

#iterate_all_params(params)
#e,d =learn_embeddings(params4)
print(evaluate("data/embeddings.npy","data/dictionary.npy"))