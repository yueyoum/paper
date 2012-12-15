# -*- coding: utf-8 -*-


from xml.sax.saxutils import unescape

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


__all__ = ['BaseConvert', ]

class BaseConvert(object):
    def convert(self, source):
        raise NotImplementedError
    
    def highlight_code(self, code_name, code_content):
        lexer = get_lexer_by_name(code_name.lower())
        return highlight(unescape(code_content), lexer, HtmlFormatter())
