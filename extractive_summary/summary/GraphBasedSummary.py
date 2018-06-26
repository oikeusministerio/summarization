import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from nltk import word_tokenize, sent_tokenize


class GraphBasedSummary:

    def __init__(self, text, threshold=0.1):
        self.sentences = self.split_document_to_sentences(text)
        assert len(self.sentences) < 400
        self.dumping_factor = 0.85
        self.threshold = threshold

    def split_document_to_sentences(self, text):
        sentences = sent_tokenize(text, language="finnish")
        sentences = [s for s in sentences if len(s) > 3]
        # add id to give order for sentences later
        return pd.DataFrame({'position': np.arange(len(sentences)), 'sentence': np.array(sentences)})

    def power_iteration(self, N, M, num_simulations):
        p_last = 1 / N * np.ones(N)
        p = p_last
        t = 0
        while True:
            t += 1
            p = M.T.dot(p_last)
            delta = np.linalg.norm(p - p_last)
            p_last = p
            if delta < 1e-10 or t > num_simulations:
                break
        return p

    def lex_rank(self, matrix, threshold):
        """
        Algorithm 3 in the article
        """
        N = matrix.shape[0]
        degree = np.zeros(N)
        for i in range(N):
            for j in range(N):
                if matrix[i, j] > threshold:
                    matrix[i, j] = 1
                    degree[i] += 1
                else:
                    matrix[i, j] = 0
        for i in range(N):
            for j in range(N):
                matrix[i, j] = matrix[i, j] / degree[i]

        return self.power_iteration(N, matrix, 100)

    def get_ranking(self, threshold):
        matrix = self.creer_matrice_adjance(self.sentences['sentence'])
        return self.lex_rank(matrix, threshold)


    def sentence_cosine_similarity(self, w1, w2):
        """
        :w1: np.array or words
        :w2: np.array or words
        """
        words = set()
        for w in w1:
            words.add(w)
        for w in w2:
            words.add(w)
        res = np.zeros((2, len(words)))
        for i, w in enumerate(words):
            res[0][i] = np.count_nonzero(w1 == w)
            res[1][i] = np.count_nonzero(w2 == w)
        return (cosine_similarity(res)[0][1])

    def find_LCS(self, string1, string2):
        """
        :param word to be compared:
        :param word to be compared:
        :return the length of the longest common subsequence (LCS):
        """
        answer = ""
        len1, len2 = len(string1), len(string2)
        for i in range(len1):
            match = ""
            for j in range(len2):
                if (i + j < len1 and string1[i + j] == string2[j]):
                    match += string2[j]
                else:
                    if (len(match) > len(answer)): answer = match
                    match = ""
        return len(answer)

    def LCS(self, s1, s2):
        """
        :param s1: sentece
        :param s2: sentence
        :return: longest
        """
        res = 1 / len(s1)
        res *= sum([max([self.find_LCS(word1, word2) for word2 in s2]) for word1 in s1])
        return res

    def similarity(self, s1, s2):
        w1 = np.array(word_tokenize(s1.lower()))
        w2 = np.array(word_tokenize(s2.lower()))
        return self.sentence_cosine_similarity(w1, w2)

    def creer_matrice_adjance(self, sentences):
        N = len(sentences)
        matrice = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i == j:
                    matrice[i][j] = 1
                    continue
                p1 = sentences[i]
                p2 = sentences[j]
                matrice[i][j] = self.similarity(p1, p2)
        return matrice

    def take_paragraphs_until(self, df, chars):
        res = []
        res_len = 0
        i = 0
        while (i < len(df) and res_len + len(df["sentence"].iloc[i]) < chars):
            res.append((df["sentence"].iloc[i], df["position"].iloc[i]))
            res_len += len(df["sentence"].iloc[i])
            i += 1
        res = np.array(res)
        if len(res) == 0:
            return np.array([]), np.array([]), 0
        resume = pd.DataFrame({'sentence': res[:, 0], 'position': res[:, 1]})
        resume['position'] = pd.to_numeric(resume['position'])
        ordered_resume = resume.sort_values(by='position', ascending=True)
        return ordered_resume['sentence'].values, ordered_resume['position'].values, i

    def summarize(self, summary_length=1000, return_ranking=False):
        """
        :param threshold: minimum similarity value between two sentences
        :param summary_length: number of characters to use in summary
        (ATTENTION! As dealing with sentences of different size, the summary procuded will not propably be exactly that length.)
        :return: summary
        """
        ranking = self.get_ranking(self.threshold)
        df = self.sentences
        df['ranking'] = ranking
        ordered = df.sort_values(by='ranking', ascending=False)
        sentences, positions, i = self.take_paragraphs_until(ordered, summary_length)
        if return_ranking:
            return sentences, positions, ordered['ranking'][:i]
        return sentences, positions