# %%
import re
import time
from pathlib import Path

import nltk
import pandas as pd
import pendulum
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def compare_segments(input_A="Songs_database.csv", input_B="output.csv", compare_A="Lyrics", compare_B="title", return_A=["Song_title"], return_B=["title", "link"], top_results=3, similarity_threshold=0.25, output_file="top_news_songs.csv", model_use='paraphrase-mpnet-base-v2'):
    """[Encodes Sentences using transformers, calculates cosine similarity. Records/updates top results higher then threshold.]

    Args:
        input_A (str, optional): [filepath of csv A to compare]. Defaults to "".
        input_B (str, optional): [filepath of csv B to compare]. Defaults to "output.csv".
        compare_A (str, optional): [Column from input A to compare]. Defaults to "Lyrics".
        compare_B (str, optional): [Column from input B to compare]. Defaults to "title".
        return_A (list, optional): [List of columns to return from input A]. Defaults to ["Song_title"].
        return_B (list, optional): [List of columns to return from input B]. Defaults to ["title", "link"].
        top_results (int, optional): [Top n results with highest similarity score to return (higher then similarity_threshold)]. Defaults to 3.
        similarity_threshold (float, optional): [similarity score threshold. Only scores higher then threshold are returned]. Defaults to 0.25.
        output_file (str, optional): [filepath of csv DB where to store results]. Defaults to "top_news_songs.csv".
        model_use (str, optional): [SentenceTransformer to use]. Defaults to 'paraphrase-mpnet-base-v2'.
    """
    A = pd.read_csv(input_A)
    B = pd.read_csv(input_B)

    # Removing special characters and stop words from the texts
    nltk.download('stopwords')
    stop_words_l = stopwords.words('english')

    B['compare_B_c'] = B[compare_B].apply(lambda x: " ".join(re.sub(
        r'[^a-zA-Z]', ' ', w).lower() for w in x.split() if re.sub(r'[^a-zA-Z]', ' ', w).lower() not in stop_words_l))

    A['compare_A_c'] = A[compare_A].apply(lambda x: " ".join(re.sub(
        r'[^a-zA-Z]', ' ', w).lower() for w in x.split() if re.sub(r'[^a-zA-Z]', ' ', w).lower() not in stop_words_l))

    sen_B = list(B.compare_B_c.values)
    sen_A = list(A.compare_A_c.values)
    model = SentenceTransformer(model_use)
    # Encoding:
    print("Encoding embeddings...")
    start_time = time.time()

    sen_embeddings_B = model.encode(sen_B)
    shape_B = sen_embeddings_B.shape
    sen_embeddings_A = model.encode(sen_A)
    shape_A = sen_embeddings_A.shape

    print("Embeddings encoded in ", "- %s seconds -" %
          (time.time() - start_time), str(shape_A), str(shape_B))
    # Similarity Matrix
    similarity_matrix = cosine_similarity(
        sen_embeddings_B, sen_embeddings_A)

    df_similarity_matrix = pd.DataFrame(data=similarity_matrix)

    similarity_A = df_similarity_matrix.max(
        axis=0).sort_values(ascending=False).head(top_results)
    similarity_A = similarity_A[similarity_A > similarity_threshold].dropna()

    similarity_B = df_similarity_matrix.max(
        axis=1).sort_values(ascending=False).head(top_results)
    similarity_B = similarity_B[similarity_B > similarity_threshold].dropna()
    # Format Result
    result = pd.DataFrame(
        data=[], columns=["Index_A", "Index_B", "Similarity"])

    result["Index_A"] = similarity_A.index
    result["Similarity"] = similarity_A.values
    result["Index_B"] = similarity_B.index

    for entry in return_A:
        result[entry] = A[entry].iloc[result["Index_A"].values].values

    for entry in return_B:
        result[entry] = B[entry].iloc[result["Index_B"].values].values

    result["Timestamp"] = str(pendulum.now('Europe/London'))
    result["Latest"] = "Y"

    # Check if files exists (adds to existing one), else create a new one
    my_file = Path(output_file)
    if my_file.is_file():
        results_old = pd.read_csv(output_file)
        results_old["Latest"] = "N"
        result = pd.concat([result, results_old])
        result.to_csv(output_file, index=False)
        print("DB updated")
    else:
        result.to_csv(output_file, index=False)
        print("DB created")
