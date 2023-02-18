#!/usr/bin/env python3

import subprocess
from xml.etree import ElementTree
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

result = subprocess.run(['mkvextract', args.filename, 'tags'], stdout=subprocess.PIPE)
tagroot = ElementTree.fromstring(result.stdout)
print(tagroot.findall("./Tag"))
