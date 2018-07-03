
import os
import sys
sys.path.append(os.path.abspath("../")) # not maybe the best way to structure but MVP
from summarization.embeddings.EmbeddingLearner import EmbeddingLearner

params = {"batch_size":128,
          "embedding_size":128,
          "skip_window": 1,
          "num_skips": 2,
          "num_sampled":64,
          "num_steps": 100001,
          "vocabulary_size": 80000}

assert len(sys.argv) == 3

source_dir = sys.argv[1] #"../judgments/data"
destination_dir = sys.argv[2] #"data/"
learner = EmbeddingLearner(source_dir, destination_dir, params)
learner.run()