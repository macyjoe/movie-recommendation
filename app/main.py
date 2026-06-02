from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.recommender import (
    load_model,
    get_recommendations,
    search_movies,
    get_movie_by_id,
    get_popular_movies,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("추천 모델 로딩 중...")
    load_model()
    print("모델 로딩 완료!")
    yield


app = FastAPI(
    title="Movie Recommendation API",
    description="콘텐츠 기반 영화 추천 서비스 (TF-IDF + 코사인 유사도)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 응답 스키마 ────────────────────────────────────────────────

class MovieBase(BaseModel):
    id: int
    title: str
    genres: list[str]
    vote_average: float
    overview: str
    poster_path: str
    release_date: str


class MovieDetail(MovieBase):
    vote_count: int
    directors: list[str]
    cast: list[str]
    keywords: list[str]


class RecommendedMovie(MovieBase):
    similarity: float


class RecommendResponse(BaseModel):
    query_title: str
    recommendations: list[RecommendedMovie]


# ── 엔드포인트 ────────────────────────────────────────────────

@app.get("/", summary="헬스 체크")
def root():
    return {"status": "ok", "message": "Movie Recommendation API가 실행 중이에요!"}


@app.get("/movies/popular", response_model=list[MovieBase], summary="인기 영화 목록")
def popular(limit: int = Query(default=20, ge=1, le=100)):
    return get_popular_movies(limit)


@app.get("/movies/search", response_model=list[MovieBase], summary="영화 검색")
def search(q: str = Query(..., min_length=1), limit: int = Query(default=20, ge=1, le=100)):
    results = search_movies(q, limit)
    if not results:
        raise HTTPException(status_code=404, detail=f"'{q}'에 해당하는 영화를 찾을 수 없어요.")
    return results


@app.get("/movies/{movie_id}", response_model=MovieDetail, summary="영화 상세 정보")
def movie_detail(movie_id: int):
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"ID {movie_id} 영화를 찾을 수 없어요.")
    return movie


@app.get("/recommend", response_model=RecommendResponse, summary="영화 제목으로 추천")
def recommend(
    title: str = Query(..., min_length=1, description="추천 기준 영화 제목"),
    top_n: int = Query(default=10, ge=1, le=50, description="추천 개수"),
):
    results = get_recommendations(title, top_n)
    if not results:
        raise HTTPException(status_code=404, detail=f"'{title}' 영화를 찾을 수 없어요.")
    return {"query_title": title, "recommendations": results}
