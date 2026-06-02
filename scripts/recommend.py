import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

def build_model():
    print("데이터 불러오는 중...")
    df = pd.read_csv("../data/movies_processed.csv", encoding="utf-8-sig")

    # 리스트 컬럼 변환
    for col in ["genres", "directors", "cast", "keywords"]:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # TF-IDF 벡터화 (tags 컬럼 기반)
    print("TF-IDF 벡터화 중...")
    tfidf = TfidfVectorizer(max_features=5000, stop_words="english")
    tfidf_matrix = tfidf.fit_transform(df["tags"].fillna(""))

    # 코사인 유사도 계산
    print("코사인 유사도 계산 중...")
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 인덱스 맵 (영화 제목 → 인덱스)
    indices = pd.Series(df.index, index=df["title"]).drop_duplicates()

    # 모델 저장
    os.makedirs("../data", exist_ok=True)
    with open("../data/cosine_sim.pkl", "wb") as f:
        pickle.dump(cosine_sim, f)
    with open("../data/indices.pkl", "wb") as f:
        pickle.dump(indices, f)
    df.to_csv("../data/movies_processed.csv", index=False, encoding="utf-8-sig")

    print("모델 저장 완료!")
    return df, cosine_sim, indices


def recommend(title, df, cosine_sim, indices, top_n=10):
    # 입력한 영화가 없을 경우
    if title not in indices:
        # 부분 일치 검색
        matches = [t for t in indices.index if title.lower() in t.lower()]
        if not matches:
            return f"'{title}' 영화를 찾을 수 없어요."
        title = matches[0]
        print(f"'{title}' 로 검색합니다.")

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]  # 자기 자신 제외

    movie_indices = [i[0] for i in sim_scores]
    result = df.iloc[movie_indices][["title", "genres", "vote_average", "overview"]].copy()
    result["similarity"] = [round(s[1], 3) for s in sim_scores]

    return result


if __name__ == "__main__":
    df, cosine_sim, indices = build_model()

    # 테스트
    print("\n=== 추천 테스트 ===")
    test_title = df["title"].iloc[0]
    print(f"'{test_title}' 와 비슷한 영화 TOP 5:")
    result = recommend(test_title, df, cosine_sim, indices, top_n=5)
    if isinstance(result, pd.DataFrame):
        for _, row in result.iterrows():
            print(f"  - {row['title']} (유사도: {row['similarity']}, 평점: {row['vote_average']})")
    else:
        print(result)
