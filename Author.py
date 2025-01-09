class Author:
    # Initialisation de la classe Author
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = []

    # Affichage de l'objet
    def __str__(self):
        return f"{self.name} ({self.ndoc} docs)"

    # Ajout d'un document à la production de l'auteur
    def add(self, doc):
        self.production.append(doc)
        self.ndoc += 1
    # Retourne le nombre de documents de l'auteur
    def nb_docs(self):
        return self.ndoc
    # Retourne la moyenne de mots par document de l'auteur
    def get_moyenne(self):
        return sum([len(doc.texte.split()) for doc in self.production]) / self.ndoc if self.ndoc > 0 else 0
