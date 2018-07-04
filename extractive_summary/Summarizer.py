
from extractive_summary.summary.GraphBasedSummary import GraphBasedSummary
from extractive_summary.summary.EmbeddingsBasedSummary import EmbeddingsBasedSummary
from extractive_summary.DocumentParser import DocumentParser
from tools.exceptions import SummarySizeTooSmall

from multiprocessing.dummy import Pool as ThreadPool
import itertools

def summarization_job(summarizer, parsed_document, method, summary_length, minimum_distance, title):
    try:
        return summarizer.summarize(parsed_document[title], method, summary_length, minimum_distance)
    except SummarySizeTooSmall as e:
        print("with title " + str(title) + ", " + str(e))
        return('', [])


class MultithreadSummary:

    thread_count = 5

    def __init__(self, summarizer):
        self.pool = ThreadPool(MultithreadSummary.thread_count)
        self.summarizer = summarizer

    def summarize(self, parsed_document, titles, method, summary_length, minimum_distance):
        params = zip(itertools.repeat(self.summarizer), \
                     itertools.repeat(parsed_document), \
                     itertools.repeat(method), \
                     itertools.repeat(summary_length), \
                     itertools.repeat(minimum_distance), \
                     titles) # this is only non constant for summarization_job
        results = self.pool.starmap(summarization_job, params)
        summaries = {}
        for i,res in enumerate(results):
            title = titles[i]
            summary, positions = res
            summaries[title] = {'summary': summary, 'positions': positions}

        return summaries

    def close(self):
        self.pool.close()
        self.pool.join()

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

    # def graph_summary_with_ranking(self, text, length, threshold):
    #     summarizer = GraphBasedSummary(text, threshold=threshold)
    #     sentences, positions, ranking = summarizer.summarize(summary_length=length, return_ranking=True)
    #     ranking = ranking.round(3)
    #     return " ".join(sentences), [int(p) for p in positions], ranking.values.tolist()

    def summary_from_file(self, file, method, summary_length, minimum_distance):
        parser = DocumentParser(file)
        if '.docx' in file.filename:
            parsed_document, titles = parser.parse_docx()
        elif '.txt' in file.filename:
            parsed_document, titles = parser.parse_txt()
        else:
            raise ValueError('File extension not supported.')

        summarizer = self
        ms = MultithreadSummary(summarizer)
        summaries = ms.summarize(parsed_document, titles,method,summary_length, minimum_distance)
        summaries['success'] = True
        summaries['titles'] = titles
        return summaries