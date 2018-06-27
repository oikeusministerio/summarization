
# coding: utf-8

# In[ ]:

import numpy as np
import matplotlib.pyplot as plt
from nltk import word_tokenize
import sys
import os
sys.path.append(os.path.abspath('../'))
from summarization.tools.tools import load_data
from sklearn.feature_extraction.text import CountVectorizer

assert len(sys.argv) > 1, "please give a path where to save file"

destination_path = sys.argv[1]
assert os.path.isdir(os.path.split(destination_path)[0]), "Not exists"


texts = load_data('judgements/data', N=-1)
lower_case_texts = texts['text'].apply(lambda text: text.lower())

vectorizer = CountVectorizer(min_df=5)
vectorizer.fit(lower_case_texts)
vocabulary = vectorizer.vocabulary_

words = lower_case_texts.apply(lambda text: [w for w in word_tokenize(text, language="finnish") if len(w) >= 2 and w in vocabulary])


print('Words tokenized')
# In[ ]:


def count_words(old_total,  word_list):
    old_total.update(word_list)
    #new_common = old_common.intersection(word_list)
    return (old_total, len(old_total))

total_vocabulary = set()
#common_words = set()
#common_words.update(words[0])

count_results = []
count_results.append((total_vocabulary, 0))
for i in range(len(words)):
    #total, common, _, __ = count_results[i]
    if i % 100 == 0:
        print(i)
    total, _ = count_results[i]
    count_results.append(count_words(total, words[i]))

results = np.array(count_results)
totals = results[:, 1]
#commons = results[:, 3]


# In[ ]:


plt.plot(range(len(totals)), totals)
plt.title("Uniikkien sanojen määrä \n")
plt.xlabel("Päätöksien määrä")
plt.ylabel("Sanojen määrä")
plt.savefig(destination_path)


# In[ ]:


len(total_vocabulary)

