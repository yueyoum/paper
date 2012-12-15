# -*- coding: utf-8 -*-

import re

import markdown


from base import BaseConvert


__all__ = ['MarkDownConvert', ]

PRE_PATTERN = re.compile('<pre><code>.+?</code></pre>', re.DOTALL)
CODE_PATTERN = re.compile('`{3}(.+?)\n(.+?)`{3}', re.DOTALL)

class MarkDownConvert(BaseConvert):
    def convert(self, source):
        if not isinstance(source, unicode):
            source = source.decode('utf-8')
        md = markdown.markdown(source, safe_mode=False)
        pre_areas = PRE_PATTERN.findall(md)
        for pre in pre_areas:
            _code = CODE_PATTERN.search(pre)
            if _code is None:
                continue
            
            code_name, code_content = _code.groups()
            
            converted = self.highlight_code(code_name, code_content)
            md = md.replace(pre, converted)
            
        return md
