
import json
import io
import requests
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from tools.conll_to_df import conll_df
import pandas as pd
import numpy as np

def get_category_mapping(series):
    return dict(zip(series.cat.categories, range(len(series.cat.codes))))

class NameExtractor:
    """
    Extracts names from text using TurkuNLP/Dependency Parser.
    """

    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.dependency_parser_url = config['dependency_parser_url'] # "http://127.0.0.1:9876"

    def extract_names(self, parsed_document, titles):
        names = []
        for title in titles:
            section = parsed_document[title]

            headers = {'Content-type': 'text/plain; charset=utf-8'}
            response = requests.post(self.dependency_parser_url, data=section.encode('utf-8'), headers=headers)
            data = conll_df(response.text)
            data.w = data.w.astype(str)
            data.l = data.l.astype(str)
            data.reset_index(level=['s','i'], inplace=True)

            word_index = pd.Series(range(data.shape[0]))
            tmp_data = pd.DataFrame({
                'x': data.x.values,
                'w': data.w.values,
                's':data.s.values,
                'i':data.i.values,
                'word_index': word_index})

            next_word_index = np.append(tmp_data[tmp_data.x == 'PROPN'].word_index.values[1:], 0)
            next_propns = tmp_data[tmp_data.x == 'PROPN'].word_index - next_word_index
            propns_to_combine = next_propns[next_propns == -1].index

            combinations = data.w.iloc[propns_to_combine] + ' ' + data.w.iloc[(propns_to_combine + 1)]

            tmp_data.w.iloc[propns_to_combine] = combinations.values
            tmp_data = tmp_data.drop(tmp_data.iloc[propns_to_combine + 1].index)
            #CONTINUE WITH TMP DATA
            choose_word_or_lemma = lambda pair: pair[1] if pair[1].istitle() else pair[0]

            propns = data[data.x == 'PROPN'][['w','l']].apply(choose_word_or_lemma, axis=1).values



            vectorizer = CountVectorizer(analyzer='word', ngram_range=(2, 3))
            vectorizer.fit_transform([section])
            ngrams = vectorizer.vocabulary_

            for propn in propns:

                matches = [ng for ng in ngrams if propn.lower() in ng]
                words = [word for match in matches for word in match.split() if word != propn.lower()]
                counter = Counter(words)

                pair = counter.most_common(1)
                ner = propn + ' ' + pair[0][0].title() if len(pair) == 1 else propn
                names.append(ner)
        return names