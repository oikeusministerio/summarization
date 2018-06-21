
import os
import unittest
from .DocumentParser import DocumentParser

class TestDocumentParser(unittest.TestCase):

    def test_paragraph_count(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        with open(dirname + '/testi.docx', 'rb') as f:
            parser = DocumentParser(f)
        f.close()
        self.assertEqual(parser.paragraph_count(), 6)

        with open(dirname + '/testi2.docx', 'rb') as f:
            parser = DocumentParser(f)
        f.close()
        self.assertEqual(parser.paragraph_count(), 34)

    def test_parser(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        with open(dirname + '/testi.docx', 'rb') as f:
            parser = DocumentParser(f)
        f.close()

        parsed,titles = parser.parse()
        self.assertEqual(len(titles), 2)
        self.assertTrue(titles[0] not in parsed[titles[0]])

        with open(dirname + '/testi2.docx', 'rb') as f:
            parser = DocumentParser(f)
        f.close()
        parsed2, titles2 = parser.parse()
        self.assertEqual(len(titles2), 0)
        self.assertTrue("Sisalto" in parsed2)

if __name__ == '__main__':
    unittest.main()