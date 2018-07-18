import unittest
from .NameExtractor import NameExtractor
from .DocumentParser import DocumentParser
from tools.tools import load_data
import tempfile
import os.path

class TestNameExtractor(unittest.TestCase):
    """
    This test uses data that is fetched by script
    judgments/fetch.py. Please run it first to get
    loca copies of data used here.
    """

    def test_extracting_names(self):
        extractor = NameExtractor()

        with open('judgments/data/1999_78.txt', 'rb') as file:
            text = file.read().decode('utf8')

            names_found, _ = extractor.extract_names(text)

            names = ['Tartto Viro', 'Venäjä', 'Suomi', \
                     'Haarmann', 'Tulokas', 'Hidén', 'Palaja', 'Krogerus', 'Elisa Mäntysaari']

            count = 0
            for nf in names_found:
                for n in names:
                    if n in nf:
                        count += 1
            self.assertLessEqual(len(names) - count, len(names) // 4) # max 1/4 not found

        with open('judgments/data/2000_67.txt', 'rb') as file:
            text = file.read().decode('utf8')

            names_found, _ = extractor.extract_names(text)

            names = ['Erkki','Olavi','Närhi', 'Art-Pine', 'Martti', 'Kääriäinen', 'Eija', 'Kääriäinen','Peltonen', \
                     'Aarnio-Helmisen', 'Heinonen', 'Nikkarinen', 'Wirilander', 'Möller', 'Välimäki', 'Pasi Kumpula']
            count = 0
            for nf in names_found:
                for n in names:
                    if n in nf:
                        count += 1
            self.assertLessEqual(len(names) - count, len(names) // 4) # max 1/4 not found

    def test_that_super_long_words_not_extracted(self):
        extractor = NameExtractor()

        data = load_data('judgments/data', N=2)
        for i, row in data.iterrows():
            text = row['text']
            names_found, _ = extractor.extract_names(text)

            for name in names_found:
                self.assertLess(len(name), 100, 'name: ' + name) # maybe some words are even longer :D

    def test_extract_names_multifile(self):
        extractor = NameExtractor()

        file_contents ={'filu1.docx': 'Ensimmäinen nimi on Pekka, toinen on Virtanen. Siis Pekka on nimi ja Virtanen sukunimi. Jack Bauer ei valita.', \
                        'kakkos-filu.txt': 'Ensimmäinen nimi on Pekka, toinen on Virtanen. Siis Pekka on nimi ja Virtanen sukunimi. Jack Bauer ei valita.'}
        filenames = ['filu1.docx', 'kakkos-filu.txt']
        results = extractor.extract_names_directory(file_contents, filenames, extract_names_uniformly=True, names_max_N=4)
        for i in range(len(results)):
            self.assertTrue('Pekka' in results[i])
            self.assertTrue('Virtanen' in results[i])

        # when taking not uniformely, next one will dominate.
        file_contents['bauer_file.docx'] = 'Jack Bauer kerran. Jack Bauer vielä kerran. Jack Bauer vielä kerran. Jack Bauer vielä kerran. Ja Virtanen.'
        filenames.append('bauer_file.docx')
        results2 = extractor.extract_names_directory(file_contents, filenames, extract_names_uniformly=False,
                                                    names_max_N=4)
        for i in range(len(results2)):
            self.assertTrue('Jack Bauer' in results2[i])
            self.assertTrue('Virtanen' in results2[i])

    def test_drawing_graph(self):
        extractor = NameExtractor()
        files = {'filenames':['filu1.docx', 'kakkos-filu.txt'], 'filu1.docx':['Hessu', 'Heluna'], 'kakkos-filu.txt':['Heluna', 'Musta-Pekka']}

        with tempfile.NamedTemporaryFile(suffix='.gv') as tmp_file:
            filename = tmp_file.name
            graph_file = extractor.create_graph(tmp_file.name,files)
            self.assertTrue(os.path.isfile(filename))
            self.assertTrue(os.path.isfile(graph_file))

        self.assertFalse(os.path.isfile(filename))
        self.assertTrue(os.path.isfile(graph_file))
        os.remove(graph_file)
        self.assertFalse(os.path.isfile(graph_file))