
from extractive_summary.summary.GraphBasedSummary import GraphBasedSummary
from extractive_summary.summary.EmbeddingsBasedSummary import EmbeddingsBasedSummary

class Summarizer:

    def __init__(self, config):
        self.dictionary_file = config["dictionary_file"]

    def summarize(self, text, method, length, threshold=None):
        summary_method = GraphBasedSummary(text, threshold=threshold) \
            if method == "graph" else EmbeddingsBasedSummary(text, dictionary_file=self.dictionary_file)
        sentences, positions = summary_method.summarize(summary_length=length)
        return " ".join(sentences), [int(p) for p in positions]

    def embedding_summary_with_nearest_neighbors(self, text, length):
        summarizer = EmbeddingsBasedSummary(text,  dictionary_file=self.dictionary_file)
        sentences, positions, words, neighbors = summarizer.summarize(summary_length=length, return_words=True)
        return " ".join(sentences), [int(p) for p in positions], words, neighbors