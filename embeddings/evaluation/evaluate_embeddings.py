
import json
import os
import sys
sys.path.append(os.path.abspath("../")) # not maybe the best way to structure but MVP
from summarization.embeddings.evaluation.Evaluator import Evaluator

with open('config.json', 'r') as f:
    config = json.load(f)
    dico_file = config['dictionary_file']
    embed_file = config['embeddings_file']
    evaluator = Evaluator(embed_file, dico_file, "embeddings/evaluation/FinnSim_judgment_scores.csv")
    print(evaluator.evaluate())