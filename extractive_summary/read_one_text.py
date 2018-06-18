
import sys
import os
sys.path.append(os.path.abspath('../tools'))
from tools import load_data
import nltk
nltk.download('punkt') # this one installs rules for punctuation
import os.path


fname = "../judgements/data"
print("read data from : ", fname)
if os.path.isdir(fname):
    data = load_data('../judgements/data', N=10)

    index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    text1 = data.iloc[index]['text']
    print(text1)
else:
    print("No texts found.")