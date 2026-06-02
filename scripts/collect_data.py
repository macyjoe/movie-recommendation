import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def get_popular_movies(total_pages=50):
    movies = []

    for page in range(1, total_pages + 1):
        url = f"{BASE_URL}/movie/popular"
        params = {"api_key": API_KEY, "language": "ko-KR", "page": page}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"오류 발생 (page {page}): {response.status_code}")
            break

        data = response.json()
        movies.extend(data["results"])
        print(f"페이지 {page}/{total_pages} 수집 완료 ({len(data['results'])}편)")
        time.sleep(0.25)  # API 요청 제한 방지

    return movies


def get_movie_detail(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "ko-KR",
        "append_to_response": "credits,keywords",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


def collect_and_save():
    print("인기 영화 목록 수집 중...")
    movies = get_popular_movies(total_pages=50)
    print(f"\n총 {len(movies)}편 수집 완료. 상세 정보 수집 시작...")

    detailed = []
    for i, movie in enumerate(movies):
        detail = get_movie_detail(movie["id"])
        if detail:
            detailed.append({
                "id": detail["id"],
                "title": detail["title"],
                "overview": detail.get("overview", ""),
                "genres": [g["name"] for g in detail.get("genres", [])],
                "release_date": detail.get("release_date", ""),
                "vote_average": detail.get("vote_average", 0),
                "vote_count": detail.get("vote_count", 0),
                "popularity": detail.get("popularity", 0),
                "poster_path": detail.get("poster_path", ""),
                "directors": [
                    c["name"] for c in detail.get("credits", {}).get("crew", [])
                    if c["job"] == "Director"
                ],
                "cast": [
                    c["name"] for c in detail.get("credits", {}).get("cast", [])[:5]
                ],
                "keywords": [
                    k["name"] for k in detail.get("keywords", {}).get("keywords", [])
                ],
            })
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(movies)} 완료...")
        time.sleep(0.25)

    df = pd.DataFrame(detailed)
    os.makedirs("../data", exist_ok=True)
    df.to_csv("../data/movies_raw.csv", index=False, encoding="utf-8-sig")
    print(f"\n저장 완료: data/movies_raw.csv ({len(df)}편)")
    return df


if __name__ == "__main__":
    collect_and_save()
