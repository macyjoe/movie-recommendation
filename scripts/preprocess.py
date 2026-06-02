import pandas as pd
import ast
import os

def preprocess():
    print("데이터 불러오는 중...")
    df = pd.read_csv("../data/movies_raw.csv", encoding="utf-8-sig")
    print(f"원본 데이터: {len(df)}편")

    # 1. 결측값 처리
    df["overview"] = df["overview"].fillna("")
    df["genres"] = df["genres"].fillna("[]")
    df["directors"] = df["directors"].fillna("[]")
    df["cast"] = df["cast"].fillna("[]")
    df["keywords"] = df["keywords"].fillna("[]")

    # 2. 문자열로 저장된 리스트 → 진짜 리스트로 변환
    for col in ["genres", "directors", "cast", "keywords"]:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # 3. 추천에 쓸 태그 컬럼 생성 (장르 + 감독 + 출연진 + 키워드 + 줄거리)
    def make_tags(row):
        genres = " ".join(row["genres"])
        directors = " ".join(row["directors"])
        cast = " ".join(row["cast"][:3])  # 주연 3명만
        keywords = " ".join(row["keywords"][:5])  # 키워드 5개만
        overview = row["overview"][:200]  # 줄거리 앞 200자만
        return f"{genres} {directors} {cast} {keywords} {overview}"

    df["tags"] = df.apply(make_tags, axis=1)

    # 4. 평점 낮거나 투표 수 적은 영화 필터링
    df = df[df["vote_count"] >= 50]
    df = df[df["vote_average"] >= 5.0]
    print(f"필터링 후 데이터: {len(df)}편")

    # 5. 중복 제거
    df = df.drop_duplicates(subset="id")
    print(f"중복 제거 후 데이터: {len(df)}편")

    # 6. 저장
    os.makedirs("../data", exist_ok=True)
    df.to_csv("../data/movies_processed.csv", index=False, encoding="utf-8-sig")
    print(f"\n저장 완료: data/movies_processed.csv ({len(df)}편)")
    return df

if __name__ == "__main__":
    preprocess()
