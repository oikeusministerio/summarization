
import json
import requests
from tools.conll_to_df import conll_df
import numpy as np
import re
from graphviz import Digraph

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
        self.ending_special_char = re.compile('.*[;:\.]$')
        self.contains_special_char = re.compile('.*[;:\.].*')
        self.number_mask = re.compile('.*\d.*')

    def is_clean(self,word):
        return not self.number_mask.match(word)

    def extract_names(self, parsed_document, titles):
        names = []
        for title in titles:
            section = title + parsed_document[title]
            if len(section) == 0:
                continue;

            headers = {'Content-type': 'text/plain; charset=utf-8'}
            response = requests.post(self.dependency_parser_url, data=section.encode('utf-8'), headers=headers)

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
                    to_add = self.contains_special_char.split(to_add)[0] # take only beginning
                    ner.append(to_add)
                    continue;
                if len(ner) > 0:
                    names.append(' '.join(ner))
                    ner = []

        return skip_allmost_duplicates(np.unique(names))

    def create_graph(self,destination_file, files):
        """
        :param destination_file: Temporary file, when using with clause it is removed automatically.
        It is used to create graph in .pdf format.
        :param files: contains files and their extracted names to be visualized
        :return: path to created pdf file. ATTENTION! Remember to delete this file after sent to user.
        """

        dot = Digraph(comment='Nimet eri tiedostoissa.')
        person_to_file = {}
        for i, fn in enumerate(files['filenames']):
            id = 'f-' + str(i)
            dot.node(id, fn, color='red')
            for j, person in enumerate(files[fn]['extracted_names']):
                if person in person_to_file:
                    person_to_file[person].append(id)
                else:
                    person_to_file[person] = [id]

        for i,person in enumerate(person_to_file.keys()):
            id = 'p-'+ str(i)
            dot.node(id, person, color='blue')

            for file_id in person_to_file[person]:
                dot.edge(id, file_id)

        dot.render(destination_file)
        return destination_file + '.pdf'
