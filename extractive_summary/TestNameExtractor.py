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
            parser = DocumentParser(file)
            parsed_document, titles = parser.parse_txt()

            names_found = extractor.extract_names(parsed_document, titles)

            names = ['Tartto Viro', 'Venäjä', 'Suomi', \
                     'Haarmann', 'Tulokas', 'Hidén', 'Palaja', 'Krogerus', 'Elisa Mäntysaari']

            count = 0
            for nf in names_found:
                for n in names:
                    if n in nf:
                        count += 1
            self.assertLessEqual(len(names) - count, len(names) // 4) # max 1/4 not found

        with open('judgments/data/2000_67.txt', 'rb') as file:
            parser = DocumentParser(file)
            parsed_document, titles = parser.parse_txt()

            names_found = extractor.extract_names(parsed_document, titles)

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

        data = load_data('judgments/data', N=10)
        for i, row in data.iterrows():
            text = row['text']
            with tempfile.NamedTemporaryFile(suffix='.txt') as tmp_file:
                with open(tmp_file.name, 'w') as file:
                    file.write(text);
                    file.close()
                with open(tmp_file.name, 'rb') as file:
                    parser = DocumentParser(file)
                    parsed_document, titles = parser.parse_txt()

                    names_found = extractor.extract_names(parsed_document, titles)

                    for name in names_found:
                        self.assertLess(len(name), 100, 'name: ' + name) # maybe some words are even longer :D

    def test_drawing_graph(self):
        extractor = NameExtractor()
        files = {'filenames':['filu1.docx', 'kakkos-filu.txt'], 'filu1.docx':{'extracted_names':['Hessu', 'Heluna']}, 'kakkos-filu.txt':{'extracted_names':['Heluna', 'Musta-Pekka']}}

        with tempfile.NamedTemporaryFile(suffix='.gv') as tmp_file:
            filename = extractor.create_graph(tmp_file.name,files)
            self.assertTrue(os.path.isfile(filename))
            pdf_file = filename + '.pdf'
            self.assertTrue(os.path.isfile(pdf_file))

        self.assertFalse(os.path.isfile(filename))
        self.assertTrue(os.path.isfile(pdf_file))
        os.remove(pdf_file)
        self.assertFalse(os.path.isfile(pdf_file))