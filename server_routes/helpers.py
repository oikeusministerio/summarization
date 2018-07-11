
import json
import os
import sys
sys.path.append(os.path.abspath("../"))
from summarization.extractive_summary.Summarizer import Summarizer

def create_configured_summarizer():
    with open('extractive_summary/config.json', 'r') as f:
        config = json.load(f)
        return Summarizer(config)

def return_json(dumepd_json, code):
    return dumepd_json, code, {'ContentType': 'application/json'}