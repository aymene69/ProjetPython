import numpy as np
import pandas as pd


class SearchEngine:
    def __init__(self, corpus):
        self.corpus = corpus
        self.vocab = self.const_vocab()
        self.mat_TF = self.const_mat_TF()
        self.mat_TFxIDF = self.const_mat_TFxIDF()

    def const_vocab(self):
        vocab = {}
        index = 0
        texte_nettoye = self.corpus.nettoyer_texte()

        for doc_id, texte in texte_nettoye.items():
            mots = texte.split()
            for mot in mots:
                if mot not in vocab:
                    vocab[mot] = {
                        'id': index,
                        'total_occurrences': 0,
                        'doc_count': 0
                    }
                    index += 1
                vocab[mot]['total_occurrences'] += 1

        for mot in vocab:
            vocab[mot]['doc_count'] = sum(1 for doc in texte_nettoye.values() if mot in doc)

        return vocab

    def const_mat_TF(self):
        mat_TF = [[0 for _ in range(len(self.vocab))] for _ in range(len(self.corpus.documents))]
        texte_nettoye = self.corpus.nettoyer_texte()

        for index, (doc_id, texte) in enumerate(texte_nettoye.items()):
            mots = texte.split()
            word_counts = {mot: mots.count(mot) for mot in set(mots)}

            for mot, count in word_counts.items():
                if mot in self.vocab:
                    mat_TF[index][self.vocab[mot]['id']] = count

        return np.array(mat_TF)

    def const_mat_TFxIDF(self):
        N = len(self.corpus.documents)
        idf = np.zeros(len(self.vocab))
        for mot, details in self.vocab.items():
            idf[details['id']] = np.log((1 + N) / (1 + details['doc_count'])) + 1

        mat_TFxIDF = np.zeros_like(self.mat_TF, dtype=float)
        for i in range(self.mat_TF.shape[0]):
            for j in range(self.mat_TF.shape[1]):
                mat_TFxIDF[i][j] = self.mat_TF[i][j] * idf[j]

        return mat_TFxIDF

    def similarite_cosinus(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.sqrt(np.sum(vec1 ** 2))
        norm_vec2 = np.sqrt(np.sum(vec2 ** 2))
        return dot_product / (norm_vec1 * norm_vec2) if norm_vec1 != 0 and norm_vec2 != 0 else 0

    def search(self, query, top_n=5):
        query_vector = np.zeros(len(self.vocab))
        query_words = query.lower().split()

        for word in query_words:
            if word in self.vocab:
                query_vector[self.vocab[word]['id']] += 1

        similarities = []

        for idx in range(self.mat_TFxIDF.shape[0]):
            doc_vector = self.mat_TFxIDF[idx]
            similarity = self.similarite_cosinus(query_vector, doc_vector)
            similarities.append((idx, similarity))

        similarities = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]

        results = []
        for idx, score in similarities:
            doc = list(self.corpus.documents.values())[idx]
            results.append({
                'Document': doc.titre,
                'Score': score
            })

        return pd.DataFrame(results)