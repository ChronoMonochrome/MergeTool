#!/usr/bin/env python2

import sys
from bs4 import BeautifulSoup as BeautifulSoup

html_parser = lambda html: BeautifulSoup(html, "html.parser")
print(html_parser(open("README.md").read()).text)
