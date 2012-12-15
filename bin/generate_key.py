#! /usr/bin/env python

import os
import base64

BIN_PATH = os.path.dirname(os.path.realpath(__file__))
SRC_PATH = os.path.normpath(os.path.join(BIN_PATH, '../src'))

with open(os.path.join(SRC_PATH, '_key'), 'w') as f:
    f.write( base64.b64encode(os.urandom(64)) + '\n' )