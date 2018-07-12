
import os
import unittest
from .DocumentParser import DocumentParser, count_sentences_left, split_too_long_sections
from nltk import sent_tokenize
import numpy as np

class TestDocumentParser(unittest.TestCase):

    def test_parser(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        with open(dirname + '/test_files/testi.docx', 'rb') as f:
            parser = DocumentParser(f)
            parsed, titles = parser.parse_docx()
        f.close()
        self.assertEqual(len(titles), 2)
        self.assertTrue(titles[0] not in parsed[titles[0]])

        with open(dirname + '/test_files/testi2.docx', 'rb') as f:
            parser = DocumentParser(f)
            parsed2, titles2 = parser.parse_docx()
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
                    parsed, titles = parser.parse_txt(section_min_sentence = section_min_length)
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

if __name__ == '__main__':
    unittest.main()