import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from SearchEngine import SearchEngine

# Chargement du corpus
@st.cache_data
def load_corpus(uploaded_file):
    try:
        corpus = pickle.load(uploaded_file)
        return corpus
    except Exception as e:
        st.error(f"Erreur lors du chargement du corpus : {e}")
        return None

# Configuration de la page streamlit
st.set_page_config(page_title="Moteur de recherche documentaire", layout="wide")
st.title("Moteur de recherche documentaire")

st.sidebar.title("Gestion des corpus")
corpus_files = st.sidebar.file_uploader("Importez vos corpus (fichiers .pkl)", accept_multiple_files=True)

# Chargement des corpus dans l'interface (fichiers pkl dispos dans la racine du projet)
corpora = {}
if corpus_files:
    for file in corpus_files:
        corpus = load_corpus(file)
        if corpus:
            corpora[file.name] = corpus

# Si corpus trouvés, affichage des options de recherche
if corpora:
    st.sidebar.success(f"{len(corpora)} corpus chargé(s) avec succès.")
    selected_corpus_name = st.sidebar.selectbox("Choisissez un corpus à explorer :", list(corpora.keys()))
    selected_corpus = corpora[selected_corpus_name]

    search_engine = SearchEngine(selected_corpus)

    if len(corpora) > 1:
        # Comparaison entre deux corpus
        st.header("Comparaison entre deux corpus")
        corpus1_name = st.selectbox("Corpus 1 :", list(corpora.keys()), index=0)
        corpus2_name = st.selectbox("Corpus 2 :", list(corpora.keys()), index=1)

        if corpus1_name != corpus2_name:
            corpus1 = corpora[corpus1_name]
            corpus2 = corpora[corpus2_name]

            # Comparaison des tailles de vocabulaire
            vocab1 = set(word for doc in corpus1.documents.values() for word in doc.texte.lower().split())
            vocab2 = set(word for doc in corpus2.documents.values() for word in doc.texte.lower().split())

            common_vocab = vocab1 & vocab2
            specific_vocab1 = vocab1 - vocab2
            specific_vocab2 = vocab2 - vocab1

            st.write(f"Taille du vocabulaire de {corpus1_name} : {len(vocab1)}")
            st.write(f"Taille du vocabulaire de {corpus2_name} : {len(vocab2)}")

            # Affichage des tailles de vocabulaire
            fig, ax = plt.subplots()
            # Création d'un diagramme en barres pour comparer les tailles de vocabulaire
            ax.bar([corpus1_name, corpus2_name, "Commun"],
                   [len(vocab1), len(vocab2), len(common_vocab)], color=['blue', 'orange', 'green'])
            ax.set_title("Comparaison des tailles de vocabulaires")
            ax.set_ylabel("Nombre de mots")
            st.pyplot(fig)

            specific_freq = {
                corpus1_name: len(specific_vocab1),
                corpus2_name: len(specific_vocab2)
            }
            # Affichage des mots spécifiques à chaque corpus
            fig, ax = plt.subplots()
            # Création d'un diagramme en barres horizontales pour comparer les mots spécifiques
            ax.barh(list(specific_freq.keys()), list(specific_freq.values()), color=['blue', 'orange'])
            ax.set_title("Mots spécifiques par corpus")
            ax.set_xlabel("Nombre de mots spécifiques")
            st.pyplot(fig)

    # Recherche par mots-clés
    st.header("Recherche par mots-clés")
    query = st.text_input("Entrez vos mots-clés :", value="")
    top_n = st.slider("Nombre de documents à afficher", min_value=1, max_value=20, value=5)
    search_method = st.selectbox("Méthode de recherche :", ["TFxIDF", "OKAPI-BM25"])

    if st.button("Rechercher"):
        if query.strip():
            # Appel des différentes fonctions de recherche selon la méthode choisie
            if search_method == "TFxIDF":
                results = search_engine.search_tfidf(query, top_n=top_n)
            elif search_method == "OKAPI-BM25":
                results = search_engine.search_bm25(query, top_n=top_n)

            st.write("Résultats de recherche :")
            st.dataframe(results)
        else:
            st.warning("Veuillez entrer des mots-clés pour lancer une recherche.")

    # Analyse des documents
    st.header("Filtrer les documents")
    filter_author = st.text_input("Filtrer par auteur (optionnel) :", value="")
    filter_type = st.selectbox("Filtrer par type de document :", ["Tous", "Reddit", "Arxiv"])
    sort_criteria = st.selectbox("Trier les documents par :", ["Auteur", "Date de début", "Date de fin"])

    if st.button("Appliquer les filtres"):
        filtered_docs = []
        # Filtrage des documents selon les critères choisis
        for doc_id, doc in selected_corpus.documents.items():
            if filter_author and filter_author.lower() not in str(doc.auteur).lower():
                continue
            if filter_type != "Tous" and doc.type != filter_type:
                continue
            filtered_docs.append({
                "Titre": doc.titre,
                "Auteur": doc.auteur,
                "Type": doc.type,
                "Date": doc.date
            })

        # Tri des documents selon le critère choisi
        if sort_criteria == "Auteur":
            filtered_docs = sorted(filtered_docs, key=lambda x: str(x["Auteur"]).lower())
        elif sort_criteria == "Date de début":
            filtered_docs = sorted(filtered_docs, key=lambda x: x["Date"])
        elif sort_criteria == "Date de fin":
            filtered_docs = sorted(filtered_docs, key=lambda x: x["Date"], reverse=True)
        # Affichage des documents filtrés
        st.write("Documents filtrés :")
        if filtered_docs:
            st.dataframe(pd.DataFrame(filtered_docs))
        else:
            st.warning("Aucun document trouvé avec ces filtres.")

    # Analyse comparative
    st.header("Analyse comparative")
    if st.button("Analyser le vocabulaire commun et spécifique"):
        reddit_vocab = set()
        arxiv_vocab = set()
        # Création des vocabulaires spécifiques à chaque type de document
        for doc_id, doc in selected_corpus.documents.items():
            words = set(doc.texte.lower().split())
            if doc.type == "Reddit":
                reddit_vocab.update(words)
            elif doc.type == "Arxiv":
                arxiv_vocab.update(words)

        common_words = reddit_vocab & arxiv_vocab
        specific_to_reddit = reddit_vocab - arxiv_vocab
        specific_to_arxiv = arxiv_vocab - reddit_vocab

        labels = ["Mots communs", "Mots spécifiques à Reddit", "Mots spécifiques à Arxiv"]
        sizes = [len(common_words), len(specific_to_reddit), len(specific_to_arxiv)]
        colors = ["green", "blue", "orange"]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, colors=colors)
        ax.axis("equal")
        # Affichage du diagramme circulaire
        st.pyplot(fig)

    # Évolution temporelle d'un mot
    st.header("Évolution temporelle d'un mot")
    word_to_analyze = st.text_input("Entrez un mot pour analyser son évolution :", value="")
    time_unit = st.radio("Choisissez l'unité temporelle :", ["Mois", "Année"])

    if st.button("Afficher l'évolution temporelle"):
        if word_to_analyze.strip():
            word_counts = {}
            # Calcul du nombre d'occurrences du mot dans chaque document
            for doc_id, doc in selected_corpus.documents.items():
                date = doc.date.strftime("%Y-%m") if time_unit == "Mois" else doc.date.strftime("%Y")
                count = doc.texte.lower().split().count(word_to_analyze.lower())
                word_counts[date] = word_counts.get(date, 0) + count

            dates = sorted(word_counts.keys())
            counts = [word_counts[date] for date in dates]

            plt.figure(figsize=(10, 5))
            plt.plot(dates, counts, marker="o")
            plt.title(f"Évolution temporelle de '{word_to_analyze}' ({time_unit.lower()})")
            plt.xlabel("Date")
            plt.ylabel("Occurrences")
            plt.xticks(rotation=45)
            st.pyplot(plt)
        else:
            st.warning("Veuillez entrer un mot pour afficher son évolution.")
else:
    st.warning("Veuillez importer au moins un corpus pour commencer.")
