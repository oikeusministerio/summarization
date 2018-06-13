
import pandas as pd
import os

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