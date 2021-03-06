
import os
import requests
from tools.conll_to_df import conll_df
from tools.tools import get_config
import numpy as np
import re
#from graphviz import Digraph
from dask import delayed, compute
from collections import Counter
from nltk import sent_tokenize
import math

def get_category_mapping(series):
    return dict(zip(series.cat.categories, range(len(series.cat.codes))))

def skip_allmost_duplicates(word_list):
    skip_words = set()
    word_list = np.array(word_list)
    word_list = word_list[np.argsort([len(w) for w in word_list])]
    for i, w1 in enumerate(word_list):
        for w2 in word_list[i:]:
            if w1 != w2 and w1 in w2:
                skip_words.add(w1)
    return [w for w in word_list if w not in skip_words]

def send_to_dependency_parser(path, section):
    headers = {'Content-type': 'text/plain; charset=utf-8'}
    return requests.post(path, data=section.encode('utf-8'), headers=headers)

class NameExtractor:
    """
    Extracts names from text using TurkuNLP/Dependency Parser.
    """

    def __init__(self):
        config = get_config()
        self.dependency_parser_url = config['dependency_parser_url'] # "http://127.0.0.1:9876"
        self.ending_special_char = re.compile('.*[;:\.]$')
        self.contains_special_char = re.compile('.*[;:\.].*')
        self.number_mask = re.compile('.*\d.*')

    def is_clean(self,word):
        return not self.number_mask.match(word) and not word.isupper() and len(word) > 1

    def extract_names_directory(self, files, filenames, search_person_ids, extract_names_uniformly=True ,names_max_N = 100):
        """
        Extract in parallel names for each file.
        :param files: dictionary containing file contents.
        :param filenames: list of filenames
        :param search_person_ids: search finnish person ids (in form 010101-1234)
        :param extract_names_uniformly: Boolean. If true, consider most common names of each file. If two or more files contains
            common names, in the end less than names_max_N names will be returned as duplicates are removed when merging
            the most common of each file.
        :param names_max_N: take only most frequent names, becouse it is difficult to visualize all.
        :return:
        """

        jobs = [delayed(self.extract_names(files[filename], search_person_ids)) for filename in filenames]
        results = compute(jobs)
        if len(results) == 0:
            return []
        results = results[0]
        if extract_names_uniformly:
            per_file = names_max_N // len(results)
            most_popular = set()
            for names, frequences in results:
                names = np.array(names)
                most_popular.update(names[np.argsort(frequences)[-per_file:]].tolist())
        else:
            counter = Counter()
            for names, frequences in results:
                for name, frequence in zip(names, frequences):
                    counter[name] += frequence
            most_popular = set(np.array(counter.most_common(names_max_N))[:, 0].tolist())
        # filter only most frequent names, without losing order of files.
        return [[name for name in file_result[0] if name in most_popular] for file_result in results]

    def _extract_person_ids(self, text):
        """
        Personid extracted, but not validated. The purpose of this script is not validate id but to search
        strings that are likeli in same form.

        More information in following:

        https://en.wikipedia.org/wiki/National_identification_number#Finland
        :param text:
        :return:
        """
        return re.findall('[0-9]{6}[-|+|A][A-Z0-9]{4}', text)

    def extract_names(self, text, search_person_ids = False):
        names = Counter()
        if len(text) == 0:
            return [],[];

        sentences = np.array(sent_tokenize(text, language="finnish"))
        N = len(sentences)
        iterations = math.ceil(N / 100) # send maximum 100 words at a time.

        for id_set in np.array_split(np.arange(N), iterations):
            sub_text = ' '.join(sentences[id_set])

            if search_person_ids:
                names.update(self._extract_person_ids(sub_text))

            response = send_to_dependency_parser(self.dependency_parser_url, sub_text)
            data = conll_df(response.text)
            data.w = data.w.astype(str)
            data.l = data.l.astype(str)
            data.reset_index(level=['s','i'], inplace=True)

            ner = []
            for i in range(data.shape[0]):
                word = data.iloc[i].w
                lemma = data.iloc[i].l
                role = data.iloc[i].x
                if role == 'PROPN' and self.is_clean(word):
                    to_add = lemma if lemma.istitle() else word
                    if self.ending_special_char.match(to_add):
                        to_add = to_add[:-1]
                        if len(to_add) == 0:
                            continue;
                    to_add = self.contains_special_char.split(to_add)[0] # take only beginning
                    ner.append(to_add)
                    continue;
                if len(ner) > 0:
                    names.update([' '.join(ner)])
                    ner = []
        del names[''];
        unique_names = list(names.keys())
        #unique_names = skip_allmost_duplicates(list(names.keys()))
        unique_names = [n for n in  unique_names if len(n) > 1]
        return unique_names, [names[n] for n in unique_names]
