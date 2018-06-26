
# coding: utf-8

# In[ ]:

import numpy as np
import matplotlib.pyplot as plt
from nltk import word_tokenize
import sys
import os
sys.path.append(os.path.abspath('../'))
from summarization.tools.tools import load_data





texts = load_data('judgements/data', N=-1)


# In[ ]:


words = texts['text'].apply(lambda text: [w for w in word_tokenize(text.lower(), language="finnish") if len(w) >= 2])

print('Words tokenized')
# In[ ]:


def count_words(old_total, old_common, word_list):
    old_total.update(word_list)
    new_common = old_common.intersection(word_list)
    return (old_total.copy(), new_common, len(old_total), len(new_common))

total_vocabulary = set()
common_words = set()
common_words.update(words[0])

count_results = []
count_results.append((total_vocabulary, common_words, 0, 0))
for i in range(len(words)):
    total, common, _, __ = count_results[i]
    count_results.append(count_words(total, common, words[i]))

results = np.array(count_results)
totals = results[:, 2]
commons = results[:, 3]


# In[ ]:


commons


# In[ ]:


plt.plot(range(len(totals)), totals)
plt.title("Uniikkien sanojen määrä \n")
plt.xlabel("Päätöksien määrä")
plt.ylabel("Sanojen määrä")
plt.savefig("visualisation/vocabulary_size_6423_judgements.png")


# In[ ]:


len(total_vocabulary)

