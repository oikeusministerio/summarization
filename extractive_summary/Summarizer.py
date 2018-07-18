
import pandas as pd

from extractive_summary.summary_methods.graphbased import GraphBasedSummary
from extractive_summary.summary_methods.embedding import EmbeddingsBasedSummary
from extractive_summary.DocumentParser import DocumentParser
from tools.exceptions import SummarySizeTooSmall

from dask import delayed, compute

def summarization_job(summarizer, parsed_document, method, summary_length, title):
    """
    Wrapper to catch exceptions.
    """
    try:
        s, p = summarizer.summarize(parsed_document[title], method, summary_length)
        return (title, s, p)
    except SummarySizeTooSmall as e:
        print("with title " + str(title) + ", " + str(e))
        return(title, '', [])

class ParallelSummary:
    """
    Paralleziation by Dask
    """

    def __init__(self, summarizer):
        self.summarizer = summarizer

    def summarize(self, parsed_document, original_titles, method, summary_length):
        summarize_one = lambda title : summarization_job(self.summarizer, parsed_document, method, summary_length, title)

        results = compute([delayed(summarize_one)(t) for t in original_titles]) # Dask delayed and computed
        results = pd.DataFrame(results[0],columns=['title', 'summary', 'position'])
        summaries = {}
        for i in range(results.shape[0]):
            title,summary, positions = results.iloc[i]
            summaries[title] = {'summary': summary, 'positions': positions}
        return summaries

class Summarizer:

    def __init__(self, config):
        self.dictionary_file = config["dictionary_file"]

    def summarize(self, text, method, length, threshold=None):
        summary_method = GraphBasedSummary(text, threshold=threshold) \
            if method == "graph" else EmbeddingsBasedSummary(text, dictionary_file=self.dictionary_file)
        sentences, positions = summary_method.summarize(word_count=length)
        return " ".join(sentences), [int(p) for p in positions]

    def embedding_summary_with_nearest_neighbors(self, text, length):
        summarizer = EmbeddingsBasedSummary(text,  dictionary_file=self.dictionary_file)
        sentences, positions, words, neighbors = summarizer.summarize(word_count=length, return_words=True)
        return " ".join(sentences), [int(p) for p in positions], words, neighbors


    def summary_from_file(self, file, method, summary_length):
        parser = DocumentParser(file)
        if '.docx' in file.filename:
            parsed_document, titles = parser.parse_docx()
        elif '.txt' in file.filename:
            parsed_document, titles = parser.parse_txt()
        else:
            raise ValueError('File extension not supported.')

        summarizer = self
        ms = ParallelSummary(summarizer)
        summaries = ms.summarize(parsed_document, titles,method,summary_length)
        summaries['success'] = True
        summaries['titles'] = titles
        return summaries