
import os
import sys
sys.path.append(os.path.abspath("../")) # not maybe the best way to structure but MVP
from summarization.embeddings.EmbeddingLearner import EmbeddingLearner
import argparse

params = {"batch_size":128,
          "embedding_size":128,
          "skip_window": 1,
          "num_skips": 2,
          "num_sampled":64,
          "num_steps": 100001,
          "vocabulary_size": 80000}

parser = argparse.ArgumentParser(description="Iterate over text files and learn embeddings and fit vocabulary.")
optional = parser._action_groups.pop() # Edited this line
required = parser.add_argument_group('required arguments')
required.add_argument('-source_dir', help='Path to raw text files used for learning', required=True)
required.add_argument('-destination_dir', help='Path where embeddings and dictionary will be saved.', required=True)
args = parser.parse_args()


learner = EmbeddingLearner(args.source_dir, args.destination_dir, params)
learner.run()