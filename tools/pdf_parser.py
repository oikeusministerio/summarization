
from .exceptions import ShellError

from .shell_parser import ShellParser


class PdfParser(ShellParser):
    """Extract text from pdf files using either the ``pdftotext`` from Poppler
    """

    def extract(self, filename, method='', **kwargs):
        try:
            return self.extract_pdftotext(filename, **kwargs)
        except ShellError as ex:
            raise ex

    def extract_pdftotext(self, filename, **kwargs):
        """Extract text from pdfs using the pdftotext command line utility."""
        if 'layout' in kwargs:
            args = ['pdftotext', '-layout', filename, '-']
        else:
            args = ['pdftotext', filename, '-']
        stdout, _ = self.run(args)
        return stdout
