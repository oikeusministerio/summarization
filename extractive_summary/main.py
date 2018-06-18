
import sys
from tools.tools import load_data
from summary.GraphBasedSummary import GraphBasedSummary
import nltk
nltk.download('punkt') # this one installs rules for punctuation



print("read data: ")
data = load_data('../judgements/data', N=10)

text1 = data.iloc[0]['text']
print(text1)

print("create summary")
gbs = GraphBasedSummary(text1)

summary = gbs.summarize(float(sys.argv[1]), summary_length=1000)

print(summary)