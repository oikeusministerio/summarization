
import os
from .parsing import DocumentParser, count_sentences_left, split_too_long_sections
from nltk import sent_tokenize
from werkzeug.datastructures import FileStorage

from .NameExtractor import NameExtractor
from .Summarizer import Summarizer, ParallelSummary
from .output import SummaryWriter

from tools.tools import load_data
import tempfile
import os.path
import unittest
from unittest.mock import MagicMock
import itertools
import numpy as np
import time
import json

class TestDocumentParser(unittest.TestCase):

    def test_parser(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        with open(dirname + '/test_files/testi.docx', 'rb') as f:
            parser = DocumentParser(f)
            parsed, titles = parser.parse_docx_file()
        f.close()
        self.assertEqual(len(titles), 2)
        self.assertTrue(titles[0] not in parsed[titles[0]])

        with open(dirname + '/test_files/testi2.docx', 'rb') as f:
            parser = DocumentParser(f)
            parsed2, titles2 = parser.parse_docx_file()
        f.close()
        self.assertEqual(len(titles2), 1)
        self.assertTrue("Sisalto" in parsed2)

    def test_parse_txt_file(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        for section_min_length in [30,120]:
            for filename in ['normal_text.txt', 'big_text.txt', 'average_sized_text.txt']:
                print(filename)
                with open(dirname + '/test_files/' + filename, 'rb') as f:
                    parser = DocumentParser(f)
                    parsed, titles = parser.parse_txt_file(section_min_sentence = section_min_length)
                    sentences = [s for s in sent_tokenize(str(parser.text)) if len(s) > 2]
                f.close()
                self.assertGreater(len(titles), 0)
                last_sentence = sentences[-1]
                last_section = parsed[titles[-1]]

                self.assertTrue(last_sentence in last_section)
                self.assertEqual(len(titles), len(parsed.keys()))
                for t in titles:
                    section = parsed[t]
                    self.assertLessEqual(section_min_length, len(section))

    def test_cumsums(self):
        sections = ["First section. Two sentences.", "Second section with three sents. One more. One more time.",
                    "Last but not least. Four sents. Jee. Jee jee."]
        sents, sents_left = count_sentences_left(sections)

        self.assertTrue((sents == np.array([2, 3, 4])).all())
        self.assertTrue((sents_left == np.array([9, 7, 4])).all())

    def test_split_too_long_sections(self):
        titles = ["Eka","Toka", "Kolmas"]
        sections = ["Eka blaablaa. More stuff." , "Toka blaablaa. Then even more stuff.", "And then too longue. More. More. And more."]
        parsed = dict(zip(titles, sections))

        parsed2, titles2 = split_too_long_sections(parsed, titles, 2, 2)

        self.assertEqual(len(titles2), 4)

    def test_pdf_parser(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        with open(dirname + '/test_files/seven_page.pdf', 'rb') as file:
            file_storage = FileStorage(file)
            parser = DocumentParser(file_storage)
            text = parser.parse_pdf_file()
            self.assertTrue(len(text) > 0)

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

def create_configured_summarizer():
    with open('config.json', 'r') as f:
        config = json.load(f)
        return Summarizer(config)

class TestSummarizer(unittest.TestCase):

    def test_parallel_summary(self):
        fake_summary = ('Liiba laaba.',[1])
        ids = np.arange(15)
        fake_titles = ['Title' + str(id) for id in ids]
        fake_parsed_document = dict(zip(fake_titles, itertools.repeat('blaa')))
        summarizer = Summarizer({"dictionary_file":None})
        summarizer.summarize = MagicMock(return_value=fake_summary)
        ms = ParallelSummary(summarizer)
        summaries = ms.summarize(fake_parsed_document, fake_titles, None, 10)
        for key in summaries.keys():
            self.assertTrue(summaries[key]['summary'] == fake_summary[0])

    def test_document_parser_time(self):
        tick = time.time()

        with open('extractive_summary/test_files/big_text.txt', 'rb') as file:
            file.filename = 'big_text.txt'
            summarizer = create_configured_summarizer()
            summaries = summarizer.summary_from_file(file, "embed", 15)

        tock = time.time()

        print("time in seconds: " + str(tock - tick))
        self.assertLessEqual(tock - tick, 65)

class TestSummaryWriter(unittest.TestCase):

    def test_write_docx(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        with open(dirname + '/test_files/seven_page.pdf', 'rb') as file:
            file_storage = FileStorage(file)
            summarizer = create_configured_summarizer()
            summaries = summarizer.summary_from_file(file_storage, 'embedding', 30)
            with tempfile.NamedTemporaryFile(suffix='.docx') as dest_file:
                filename = dest_file.name
                sw = SummaryWriter({'filenames':['seven_page.pdf'],'seven_page.pdf':summaries})
                sw.write_docx(filename)


if __name__ == '__main__':
    unittest.main()