
from extractive_summary.summary.GraphBasedSummary import GraphBasedSummary
from extractive_summary.summary.EmbeddingsBasedSummary import EmbeddingsBasedSummary
from extractive_summary.DocumentParser import DocumentParser
from tools.exceptions import SummarySizeTooSmall

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

    def graph_summary_with_ranking(self, text, length, threshold):
        summarizer = GraphBasedSummary(text,  threshold=threshold)
        sentences, positions, ranking = summarizer.summarize(summary_length=length, return_ranking=True)
        ranking = ranking.round(3)
        return " ".join(sentences), [int(p) for p in positions], ranking.values.tolist()

    def summary_from_file(self, file, method, summary_length, minimum_distance):
        parser = DocumentParser(file)
        if '.docx' in file.filename:
            parsed_document, titles = parser.parse_docx()
        elif '.txt' in file.filename:
            parsed_document, titles = parser.parse_txt()
        else:
            raise ValueError('File extension not supported.')
        summaries = {}
        print("titles: " + len(titles))
        for title in titles:
            print("title : " + title)
            try:
                text = " ".join(parsed_document[title])
                summary, positions = self.summarize(" ".join(parsed_document[title]), method, summary_length,
                                                               threshold=minimum_distance)
                summaries[title] = {'summary': summary, 'positions': positions}
            except SummarySizeTooSmall as e:
                print("with title " + str(title) + ", " + str(e))
                summaries[title] = {'summary': '', 'positions': []}

        summaries['success'] = True
        summaries['titles'] = titles

        return summaries