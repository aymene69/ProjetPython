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

