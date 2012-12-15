# -*- coding: utf-8 -*-

import sys
import types



if 'paper' not in sys.modules:
    paper = types.ModuleType('paper')
    paper.settings = __import__('settings')
    sys.modules['paper'] = paper
    sys.modules['paper.settings'] = paper.settings



from src.views import app
