
import pandas as pd
import os
import re
import json
from nltk import sent_tokenize
import dask.dataframe as dd

def parallel_load_data(dir_path, N=-1):
    """
    Reads the data files
    :param dir_path path to files:
    :param N how many to read, -1 means all:
    :return: dask.DataFrame with data
    """
    files = os.listdir(dir_path) if N == -1 else os.listdir(dir_path)[:N]
    data = []
    for i, filename in enumerate(files):
        if filename.endswith(".txt"):
            path = os.path.join(dir_path, filename)
            with open(path) as f:
                text = f.read()
            data.append((filename[:-4], text))
    data = pd.DataFrame(data, columns = ["id","text"])
    return dd.from_pandas(data, numpartitions = 2)

def load_data(dir_path, N=-1):
    """
    Reads the data files
    :param dir_path path to files:
    :param N how many to read, -1 means all:
    :return: pandas.DataFrame with data
    """
    files = os.listdir(dir_path) if N == -1 else os.listdir(dir_path)[:N]
    data = []
    for i, filename in enumerate(files):
        if filename.endswith(".txt"):
            path = os.path.join(dir_path, filename)
            with open(path) as f:
                text = f.read()
            data.append((filename[:-4], text))

    return pd.DataFrame(data, columns = ["id","text"])

def load_multiple_data_sources(dir_paths):
    """
    Reads the data files from given paths
    :param dir_path path to files:
    :return: dask.DataFrame with data
    """
    data = []
    for dir_path in dir_paths:
        files = os.listdir(dir_path)
        for i, filename in enumerate(files):
            if filename.endswith(".txt"):
                path = os.path.join(dir_path, filename)
                with open(path) as f:
                    text = f.read()
                data.append((filename[:-4], text))

    df = pd.DataFrame(data, columns = ["id","text"])
    return df ##dd.from_pandas(df, npartitions=2)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))

def word_is_valid(word):
    """
    Put here all rules for words that should be skipped.
    :param word:
    :return: false if word is not useful
    """
    if len(word) < 2:
        return False
    if has_numbers(word):
        return False
    return True

def sentence_tokenize(text):
    """
    Outsource tokenizing to nltk, but "hard code" some rules:
    -Upper case sequences are sentences themselfs, if they end to new line.
    :param text:
    :return:
    """
    callback = lambda pat: pat.group(0)[:-1] + '. '
    text = re.sub(r'([A-Z][ ]*)+\n', callback, text) # add . in the end of uppercase words.
    return sent_tokenize(text, language="finnish")


def get_config():
    config_file = 'config_prod.json' if os.getenv('FLASK_ENV') == 'production' else 'config.json'
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config