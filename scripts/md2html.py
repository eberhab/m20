#!/usr/bin/env python

import sys
import markdown

with open(sys.argv[1], 'r') as f:
    text = f.read()

html = markdown.markdown(text, extensions=['markdown.extensions.tables', 'footnotes'])
print(html)
