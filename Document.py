import datetime


class Document:
    # Initialisation de la classe Document
    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        try:
            self.date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        except:
            self.date = datetime.datetime.fromtimestamp(int(float(date)))
        self.url = url
        self.texte = texte
        self.type = "Document"
    # Affichage de l'objet
    def __str__(self):
        return f"{self.titre} ({self.auteur}"

    def __repr__(self):
        return f"{self.titre} ({self.auteur})"

    # Retourne le type du document
    def get_type(self):
        return self.type


class RedditDocument(Document):
    # Initialisation de la classe RedditDocument
    def __init__(self, titre, auteur, date, url, texte, nb_comments):
        super().__init__(titre, auteur, date, url, texte)
        self.nb_comments = nb_comments
        self.type = "Reddit"

    # Retourne le nombre de commentaires du document
    def get_nb_comments(self):
        return self.nb_comments

    # Modifie le nombre de commentaires du document
    def set_nb_comments(self, nb_comments):
        self.nb_comments = nb_comments

    # Affichage de l'objet
    def __str__(self):
        return (f"RedditDocument: {self.titre}, par {self.auteur}, Date: {self.date},"
                f" Nombre de commentaires: {self.nb_comments}")

    def __repr__(self):
        return (f"RedditDocument: {self.titre}, par {self.auteur}, Date: {self.date},"
                f" Nombre de commentaires: {self.nb_comments}")


class ArxivDocument(Document):
    # Initialisation de la classe ArxivDocument
    def __init__(self, titre, auteurs, date, url, texte):
        super().__init__(titre, auteurs, date, url, texte)
        self.co_auteurs = auteurs if isinstance(auteurs, list) else [auteurs]
        self.type = "Arxiv"

    # Retourne la liste des co-auteurs du document
    def get_co_auteurs(self):
        return self.co_auteurs

    # Modifie la liste des co-auteurs du document
    def set_co_auteurs(self, co_auteurs):
        self.co_auteurs = co_auteurs

    # Affichage de l'objet
    def __str__(self):
        auteurs_str = ', '.join([auteur['name'] if isinstance(auteur, dict) else auteur for auteur in self.co_auteurs])
        return f"ArxivDocument: {self.titre}, par {auteurs_str}, Date: {self.date}"

    def __repr__(self):
        auteurs_str = ', '.join([auteur['name'] if isinstance(auteur, dict) else auteur for auteur in self.co_auteurs])
        return f"ArxivDocument: {self.titre}, par {auteurs_str}, Date: {self.date}"


class DocumentFactory:
    @staticmethod
    # Crée un document de type RedditDocument ou ArxivDocument
    def create_document(doc_type, titre, auteur, date, url, texte, nb_comments=0):
        if doc_type == "reddit":
            return RedditDocument(titre, auteur, date, url, texte, nb_comments)
        elif doc_type == "arxiv":
            return ArxivDocument(titre, auteur, date, url, texte)
        else:
            raise ValueError(f"Type de document non reconnu: {doc_type}")
