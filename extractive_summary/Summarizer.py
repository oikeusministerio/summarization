
import numpy as np
import pandas as pd

from extractive_summary.summary.GraphBasedSummary import GraphBasedSummary
from extractive_summary.summary.EmbeddingsBasedSummary import EmbeddingsBasedSummary
from extractive_summary.DocumentParser import DocumentParser
from tools.exceptions import SummarySizeTooSmall

from multiprocessing.dummy import Pool as ThreadPool
import itertools

def summarization_job_tpt(summarizer, parsed_document, method, summary_length, minimum_distance, title):
    """
    tpt = thread per title
    """
    try:
        s, p = summarizer.summarize(parsed_document[title], method, summary_length, minimum_distance)
        return (title, s, p)
    except SummarySizeTooSmall as e:
        print("with title " + str(title) + ", " + str(e))
        return(title, '', [])


def summarization_job_ss(summarizer, parsed_document, method, summary_length, minimum_distance, titles):
    """
    ss = split sequential
    """
    results = []
    for title in titles:
        try:
            s,p = summarizer.summarize(parsed_document[title], method, summary_length, minimum_distance)
            results.append((title, s, p))
        except SummarySizeTooSmall as e:
            print("with title " + str(title) + ", " + str(e))
            return (title, '', [])
    return results

class MultithreadSummary:
    """
    Two modes: start new thread for each title (thread_per_title) or create few sequential ones (split_sequential).
    https://medium.com/idealo-tech-blog/parallelisation-in-python-an-alternative-approach-b2749b49a1e

    """

    thread_count = 5

    def __init__(self, summarizer, mode="split_sequantial"):
        self.pool = ThreadPool(MultithreadSummary.thread_count)
        self.summarizer = summarizer
        self.mode = mode

    def summarize(self, parsed_document, original_titles, method, summary_length, minimum_distance):
        if self.mode == "split_sequantial":
            titles = np.array_split(np.array(original_titles), MultithreadSummary.thread_count)
        else:
            titles = original_titles

        params = zip(itertools.repeat(self.summarizer), \
                     itertools.repeat(parsed_document), \
                     itertools.repeat(method), \
                     itertools.repeat(summary_length), \
                     itertools.repeat(minimum_distance), \
                     titles) # this is only non constant for summarization_job

        if self.mode == "split_sequantial":
            result_lists = self.pool.starmap(summarization_job_ss, params)
            results = []
            for res_list in result_lists:
                for res in res_list:
                    results.append(res)
        else:
            results = self.pool.starmap(summarization_job_tpt, params)

        results = pd.DataFrame(results,columns=['title', 'summary', 'position'])
        summaries = {}
        for i in range(results.shape[0]):
            title,summary, positions = results.iloc[i]
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