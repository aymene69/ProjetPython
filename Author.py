class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = []

    def __str__(self):
        return f"{self.name} ({self.ndoc} docs)"

    def add(self, doc):
        self.production.append(doc)
        self.ndoc += 1

    def nb_docs(self):
        return self.ndoc

    def get_moyenne(self):
        return sum([len(doc.texte.split()) for doc in self.production]) / self.ndoc if self.ndoc > 0 else 0
