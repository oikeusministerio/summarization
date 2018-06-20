
import numpy as np
from docx import Document

class DocumentParser:

    def __init__(self, file):
        self.document = Document(file)
        self.body_text_styles = ['Body Text','Normal']

    def parse(self):
        """
        The following is supposed when parsing :
        1) if there are titles in the text, the text will start with a title and will never end with one
        2) if there are titles in the text, text before first title or heading is skipped
        :return:
        """
        parsed_document = {}
        titles = []
        sections_starting = []
        for i, paragraph in enumerate(self.document.paragraphs):
            style = paragraph.style.name
            if style not in self.body_text_styles:
                titles.append(paragraph.text.strip())
                sections_starting.append(i)
        paragraphs = np.array([p.text for p in self.document.paragraphs])
        sections_starting.append(len(paragraphs))
        for i,title in enumerate(titles):
            pars = paragraphs[sections_starting[i]+1:sections_starting[i+1]]
            parsed_document[title] = list(pars)

        if len(titles) == 0:
            parsed_document['Sisalto'] =  list(paragraphs)

        return parsed_document, titles

    def paragraph_count(self):
        return len(self.document.paragraphs)
