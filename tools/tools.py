
import pandas as pd
import os
import re

def load_data(dir_path, N=-1):
    """
    Reads the data files
    :param dir_path path to files:
    :param N how many to read, -1 means all:
    :return: pandas.DataFrame with data
    """
    data = []
    for i, filename in enumerate(os.listdir(dir_path)):
        if N > 0 and i > N:
            break
        if filename.endswith(".txt"):
            path = os.path.join(dir_path, filename)
            with open(path) as f:
                text = f.read()
            data.append((filename[:-4], text))

    return pd.DataFrame(data, columns = ["id","text"])

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