
import json
import io
import requests
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from tools.conll_to_df import conll_df
import pandas as pd
import numpy as np
import re

def get_category_mapping(series):
    return dict(zip(series.cat.categories, range(len(series.cat.codes))))

def skip_allmost_duplicates(word_list):
    skip_words = set()
    word_list = word_list[np.argsort([len(w) for w in word_list])]
    for i, w1 in enumerate(word_list):
        for w2 in word_list[i:]:
            if w1 != w2 and w1 in w2:
                skip_words.add(w1)
    return [w for w in word_list if w not in skip_words]


class NameExtractor:
    """
    Extracts names from text using TurkuNLP/Dependency Parser.
    """

    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.dependency_parser_url = config['dependency_parser_url'] # "http://127.0.0.1:9876"
        self.special_char_mask = re.compile('.*[;:\.]$')
        self.number_mask = re.compile('.*\d.*')

    def is_clean(self,word):
        return not self.special_char_mask.match(word) and not self.number_mask.match(word)

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

            ner = []
            was_propn = False
            for i in range(data.shape[0]):
                word = data.iloc[i].w
                lemma = data.iloc[i].l
                role = data.iloc[i].x
                if role == 'PROPN' and self.is_clean(word):
                    to_add = lemma if lemma.istitle() else word
                    ner.append(to_add)
                    was_propn = True
                    continue;
                #if was_propn and role == 'NOUN':
                    #ner.append(lemma)
                was_propn = False;
                if len(ner) > 0:
                    names.append(' '.join(ner))
                    ner = []

        return skip_allmost_duplicates(np.unique(names))