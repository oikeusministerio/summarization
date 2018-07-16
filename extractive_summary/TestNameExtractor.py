import unittest
from .NameExtractor import NameExtractor
from .DocumentParser import DocumentParser

class TestNameExtractor(unittest.TestCase):

    def test_extracting_names(self):
        extractor = NameExtractor()

        with open('judgments/data/1999_78.txt', 'rb') as file:
            parser = DocumentParser(file)
            parsed_document, titles = parser.parse_txt()

            names_found = extractor.extract_names(parsed_document, titles)

            names = ['Oikeusministeriö', 'Viro', 'Viroon', 'Venäjän', 'Suomi', \
                     'A', 'Haarmann', 'Tulokas', 'Hidén', 'Palaja', 'Krogerus', 'Elisa', 'Mäntysaari']

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
            print(names_found)
            count = 0
            for nf in names_found:
                for n in names:
                    if n in nf:
                        count += 1
            self.assertLessEqual(len(names) - count, len(names) // 4) # max 1/4 not found