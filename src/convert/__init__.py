# -*- coding: utf-8 -*-

from markdown_convert import MarkDownConvert


__all__ = ['Convert', ]


MARKDOWN_FORMAT = ['md', 'markdown']

class Convert(object):
    def __new__(self, source_format):
        source_format = source_format.lower()
        if source_format in MARKDOWN_FORMAT:
            return MarkDownConvert()
        
        raise NotImplementedError