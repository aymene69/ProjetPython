import pickle
import re
import pandas as pd
from collections import defaultdict


class Corpus:
    def __init__(self, name, authors, documents, nb_docs, nb_authors):
        self.name = name
        self.authors = authors
        self.documents = documents
        self.nb_docs = nb_docs
        self.nb_authors = nb_authors

    def __str__(self):
        return f"Corpus: {self.name}, Nombre d'auteurs: {self.nb_authors}, Nombre de documents: {self.nb_docs}"

    def __repr__(self):
        return f"Corpus: {self.name}, Nombre d'auteurs: {self.nb_authors}, Nombre de documents: {self.nb_docs}"

    def show(self, n_docs=1, tri="abc"):
        if tri == "abc":
            docs = sorted(self.documents.values(), key=lambda x: x.titre)[:n_docs]
        elif tri == "123":
            docs = sorted(self.documents.values(), key=lambda x: x.date)[:n_docs]
        else:
            raise ValueError("tri doit être 'abc' ou 'date'.")

        print("\n".join(list(map(repr, docs))))

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def search(self, keyword):
        keyword = keyword.lower()
        pattern = re.compile(rf'\b{keyword}\b', re.IGNORECASE)
        results = []

        for doc_id, doc in self.documents.items():
            text = doc.texte
            words = text.split()

            for i, word in enumerate(words):
                if pattern.search(word):
                    start = max(0, i - 10)
                    end = min(len(words), i + 11)
                    context = ' '.join(words[start:end])
                    results.append(f"Document {doc.titre}: {context}")

        return results if results else "Aucun résultat trouvé."

    def concorde(self, expression, taille_contexte=10):
        motif = re.compile(rf'\b{expression}\b', re.IGNORECASE)
        resultats = []

        for doc_id, doc in self.documents.items():
            texte = doc.texte
            mots = texte.split()

            for i, word in enumerate(mots):
                if motif.search(word):
                    start = max(0, i - taille_contexte)
                    end = min(len(mots), i + taille_contexte + 1)

                    contexte_gauche = ' '.join(mots[start:i])
                    contexte_droit = ' '.join(mots[i + 1:end])
                    resultats.append([contexte_gauche, word, contexte_droit])

        df_concordance = pd.DataFrame(resultats, columns=['Contexte gauche', 'Motif trouvé', 'Contexte droit'])
        return df_concordance if not df_concordance.empty else "Aucun résultat trouvé."

    def nettoyer_texte(self):
        texte_nettoye = {}
        for doc_id, doc in self.documents.items():
            texte = doc.texte
            texte = re.sub(r'[^\w\s]', '', texte)
            texte = re.sub(r'\s+', ' ', texte)
            texte = texte.lower()
            texte_nettoye[doc_id] = texte
        return texte_nettoye

    def vocabulaire(self):
        vocab = set()
        texte_nettoye = self.nettoyer_texte()
        for doc_id, texte in texte_nettoye.items():
            mots = texte.split()
            vocab.update(mots)
        return sorted(vocab)

    def nb_occurence(self):
        occurences_totales = defaultdict(int)
        freq_documents = defaultdict(int)

        texte_nettoye = self.nettoyer_texte()
        for doc_id, texte in texte_nettoye.items():
            mots = texte.split()
            mots_uniques = set()

            for mot in mots:
                occurences_totales[mot] += 1
                if mot not in mots_uniques:
                    freq_documents[mot] += 1
                    mots_uniques.add(mot)

        df_freq = pd.DataFrame({
            'Mot': list(occurences_totales.keys()),
            'Occurences totales': list(occurences_totales.values()),
            'Document Frequency': [freq_documents[mot] for mot in occurences_totales.keys()]
        })

        df_freq = df_freq.sort_values(by='Occurences totales', ascending=False).reset_index(drop=True)

        return df_freq

    def stats(self, n=20):
        vocabulaire = self.vocabulaire()
        nb_mots_differents = len(vocabulaire)
        print(f"Nombre de mots différents dans le corpus : {nb_mots_differents}")

        df_freq = self.nb_occurence()
        print(f"Les {n} mots les plus fréquents :\n")
        print(df_freq.head(n))
