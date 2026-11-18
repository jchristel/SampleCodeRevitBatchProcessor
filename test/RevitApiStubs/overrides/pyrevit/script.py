"""pyrevit.script: get_output() returns a recording output."""
import logging


class RecordingOutput(object):
    def __init__(self):
        self.markdown = []
        self.html = []
        self.tables = []

    def print_md(self, text):
        self.markdown.append(text)

    def print_html(self, html):
        self.html.append(html)

    def print_table(self, table_data=None, title="", columns=None, formats=None, **kwargs):
        self.tables.append({"table_data": table_data, "title": title, "columns": columns, "formats": formats})


_output = RecordingOutput()


def get_output():
    return _output


def get_logger():
    return logging.getLogger("pyrevit-fake")
