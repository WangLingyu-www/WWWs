# -*- coding: utf-8 -*-
import os
from ruamel import yaml

_BASE_DIR = os.path.dirname(os.path.realpath(__file__))
print("_BASE_DIR:%s" % _BASE_DIR)
with open(os.path.join(_BASE_DIR, 'conf.yaml'), "r", encoding="utf-8") as f:
    CONF = yaml.safe_load(f)

OUT_DIR_PATH = os.path.abspath(os.path.join(_BASE_DIR, CONF.get('outDirPath')))
