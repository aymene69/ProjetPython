import praw
import urllib.request
import xmltodict
import pandas as pd
import os
import pickle
from Document import DocumentFactory
from Author import Author
from Corpus import Corpus

docs_r = []
docs_a = []


if os.path.exists('data.pkl'):
    print("data.pkl existe. Chargement des données")
    with open('data.pkl', 'rb') as f:
        df = pickle.load(f)
else:
    print("Pas de data.csv. Interrogation des API")
    reddit = praw.Reddit(client_id='CHANGEME',
                         client_secret='CHANGEME',
                         user_agent="PythonTD")

    hot_posts = reddit.subreddit('football').hot(limit=50)
    for post in hot_posts:
        docs_r.append({'user': post.author.name, 'title': post.title, 'text': post.selftext.replace('\n', ' '),
                       'date': post.created_utc, 'url': post.url, 'nb_comments': post.num_comments})

    url = 'http://export.arxiv.org/api/query?search_query=all:football&start=0&max_results=50'
    data = urllib.request.urlopen(url)
    data_parsed = xmltodict.parse(data.read().decode('utf-8'))

    for elem in data_parsed['feed']['entry']:
        authors = elem['author']
        docs_a.append({'user': authors, 'title': elem['title'], 'text': elem['summary'], 'date': elem['published'],
                       'url': elem['id'], 'nb_comments': 0})

    data = []

    def escape_special_chars(text):
        if isinstance(text, str):
            return text.replace('\t', ' ').replace('\n', ' ').replace('\r', '').replace('"', '""')
        return text

    for idx, doc in enumerate(docs_r, start=1):
        texte = escape_special_chars(doc['text']) if doc['text'] != '' else 'Pas de texte'
        auteur = (doc['user']) if doc['user'] != '' else 'Anonyme'
        date = escape_special_chars(str(doc['date'])) if doc['date'] != '' else 'Pas de date'
        url = escape_special_chars(doc['url']) if doc['url'] != '' else 'Pas d\'url'
        titre = escape_special_chars(doc['title']) if doc['title'] != '' else 'Pas de titre'
        data.append((idx, titre, auteur, texte, date, url, "reddit", doc['nb_comments']))

    for idx, doc in enumerate(docs_a, start=len(docs_r) + 1):
        texte = escape_special_chars(doc['text']) if doc['text'] != '' else 'Pas de texte'
        auteur = (doc['user']) if doc['user'] != '' else 'Anonyme'
        date = escape_special_chars(str(doc['date'])) if doc['date'] != '' else 'Pas de date'
        url = escape_special_chars(doc['url']) if doc['url'] != '' else 'Pas d\'url'
        titre = escape_special_chars(doc['title']) if doc['title'] != '' else 'Pas de titre'
        data.append((idx, titre, auteur, texte, date, url, "arxiv", doc['nb_comments']))

    df = pd.DataFrame(data, columns=["id", "titre", "auteur", "text", "date", "url", "origin", "nb_comments"])

    with open("data.pkl", 'wb') as f:
        pickle.dump(df, f)

df['text'] = df['text'].fillna('')

df = df[df['text'].apply(lambda x: len(x) >= 20)]
df = df.reset_index(drop=True)

id2doc = {}
id2aut = {}

for elem in df.itertuples():
    doc = DocumentFactory.create_document(elem.origin,
                                          elem.titre,
                                          elem.auteur,
                                          elem.date,
                                          elem.url,
                                          elem.text,
                                          elem.nb_comments)
    id2doc[elem.id] = doc

    auteur_nom = elem.auteur
    if type(auteur_nom) is list:
        for aut in auteur_nom:
            if aut['name'] not in id2aut:
                id2aut[aut['name']] = Author(aut['name'])
            id2aut[aut['name']].add(doc)
    else:
        if type(auteur_nom) is dict:
            auteur_nom = auteur_nom['name']
        if auteur_nom not in id2aut:
            id2aut[auteur_nom] = Author(auteur_nom)
        id2aut[auteur_nom].add(doc)

corpus = Corpus("Corpus sur le football", list(id2aut.values()), id2doc, len(id2doc), len(id2aut))

corpus.show()

