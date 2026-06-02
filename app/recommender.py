import pandas as pd
import pickle
import os
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

df: pd.DataFrame = None
cosine_sim = None
indices: pd.Series = None


def _parse_list_cols(dataframe: pd.DataFrame) -> pd.DataFrame:
    for col in ["genres", "directors", "cast", "keywords"]:
        if col in dataframe.columns:
            dataframe[col] = dataframe[col].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])
            )
    return dataframe


def load_model():
    global df, cosine_sim, indices

    csv_path = os.path.join(DATA_DIR, "movies_processed.csv")
    sim_path = os.path.join(DATA_DIR, "cosine_sim.pkl")
    idx_path = os.path.join(DATA_DIR, "indices.pkl")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"movies_processed.csv 파일이 없어요: {csv_path}")

    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df = _parse_list_cols(df)

    if os.path.exists(sim_path) and os.path.exists(idx_path):
        with open(sim_path, "rb") as f:
            cosine_sim = pickle.load(f)
        with open(idx_path, "rb") as f:
            indices = pickle.load(f)
    else:
        # pkl 없으면 직접 계산
        tfidf = TfidfVectorizer(max_features=5000, stop_words="english")
        tfidf_matrix = tfidf.fit_transform(df["tags"].fillna(""))
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        indices = pd.Series(df.index, index=df["title"]).drop_duplicates()

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(sim_path, "wb") as f:
            pickle.dump(cosine_sim, f)
        with open(idx_path, "wb") as f:
            pickle.dump(indices, f)


def get_recommendations(title: str, top_n: int = 10) -> list[dict]:
    if df is None:
        raise RuntimeError("모델이 로드되지 않았어요. load_model()을 먼저 호출하세요.")

    matched_title = title
    if title not in indices:
        matches = [t for t in indices.index if title.lower() in t.lower()]
        if not matches:
            return []
        matched_title = matches[0]

    idx = indices[matched_title]
    sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1: top_n + 1]

    results = []
    for i, score in sim_scores:
        row = df.iloc[i]
        results.append({
            "id": int(row.get("id", 0)),
            "title": row["title"],
            "genres": row["genres"] if isinstance(row["genres"], list) else [],
            "vote_average": float(row.get("vote_average", 0)),
            "overview": str(row.get("overview", "")),
            "poster_path": str(row.get("poster_path", "")) if pd.notna(row.get("poster_path")) else "",
            "release_date": str(row.get("release_date", "")) if pd.notna(row.get("release_date")) else "",
            "similarity": round(float(score), 3),
        })
    return results


def search_movies(query: str, limit: int = 20) -> list[dict]:
    if df is None:
        raise RuntimeError("모델이 로드되지 않았어요.")

    mask = df["title"].str.contains(query, case=False, na=False)
    matched = df[mask].head(limit)

    results = []
    for _, row in matched.iterrows():
        results.append({
            "id": int(row.get("id", 0)),
            "title": row["title"],
            "genres": row["genres"] if isinstance(row["genres"], list) else [],
            "vote_average": float(row.get("vote_average", 0)),
            "overview": str(row.get("overview", "")),
            "poster_path": str(row.get("poster_path", "")) if pd.notna(row.get("poster_path")) else "",
            "release_date": str(row.get("release_date", "")) if pd.notna(row.get("release_date")) else "",
        })
    return results


def get_movie_by_id(movie_id: int) -> dict | None:
    if df is None:
        raise RuntimeError("모델이 로드되지 않았어요.")

    row = df[df["id"] == movie_id]
    if row.empty:
        return None

    r = row.iloc[0]
    return {
        "id": int(r.get("id", 0)),
        "title": r["title"],
        "genres": r["genres"] if isinstance(r["genres"], list) else [],
        "vote_average": float(r.get("vote_average", 0)),
        "vote_count": int(r.get("vote_count", 0)),
        "overview": str(r.get("overview", "")),
        "poster_path": str(r.get("poster_path", "")) if pd.notna(r.get("poster_path")) else "",
        "release_date": str(r.get("release_date", "")) if pd.notna(r.get("release_date")) else "",
        "directors": r["directors"] if isinstance(r["directors"], list) else [],
        "cast": r["cast"] if isinstance(r["cast"], list) else [],
        "keywords": r["keywords"] if isinstance(r["keywords"], list) else [],
    }


def get_popular_movies(limit: int = 20) -> list[dict]:
    if df is None:
        raise RuntimeError("모델이 로드되지 않았어요.")

    popular = df.sort_values("vote_average", ascending=False).head(limit)
    results = []
    for _, row in popular.iterrows():
        results.append({
            "id": int(row.get("id", 0)),
            "title": row["title"],
            "genres": row["genres"] if isinstance(row["genres"], list) else [],
            "vote_average": float(row.get("vote_average", 0)),
            "overview": str(row.get("overview", "")),
            "poster_path": str(row.get("poster_path", "")) if pd.notna(row.get("poster_path")) else "",
            "release_date": str(row.get("release_date", "")) if pd.notna(row.get("release_date")) else "",
        })
    return results
