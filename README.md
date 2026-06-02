# 🎬 영화 추천 웹서비스

TMDB API로 수집한 영화 데이터를 기반으로, **콘텐츠 기반 필터링(TF-IDF + 코사인 유사도)** 으로 유사한 영화를 추천하는 웹서비스입니다.

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| 데이터 수집 | TMDB API, Python, requests |
| 데이터 처리 | pandas |
| 추천 알고리즘 | TF-IDF + 코사인 유사도 (scikit-learn) |
| 백엔드 | FastAPI, Uvicorn |
| 프론트엔드 | React (예정) |
| 배포 | 예정 |

## 📁 프로젝트 구조

```
movie-recommendation/
├── data/
│   ├── movies_raw.csv          # TMDB API 수집 원본 (1,000편)
│   ├── movies_processed.csv    # 전처리 완료 데이터 (800편)
│   ├── cosine_sim.pkl          # 코사인 유사도 행렬
│   └── indices.pkl             # 영화 제목 → 인덱스 맵
├── scripts/
│   ├── collect_data.py         # TMDB API 데이터 수집
│   ├── preprocess.py           # 데이터 전처리 및 태그 생성
│   └── recommend.py            # 추천 모델 빌드 및 테스트
├── app/
│   ├── main.py                 # FastAPI 앱 및 엔드포인트
│   └── recommender.py          # 추천 로직 (모델 로딩, 검색, 추천)
├── .env.example
├── requirements.txt
└── README.md
```

## 🚀 진행 단계

- [x] 프로젝트 초기 세팅
- [x] TMDB API 연동 및 데이터 수집 (1,000편)
- [x] 데이터 전처리 (800편 — 평점/투표수 기준 필터링)
- [x] 추천 알고리즘 개발 (TF-IDF + 코사인 유사도)
- [x] FastAPI 백엔드 API 개발
- [ ] 프론트엔드 개발 (React)
- [ ] 배포

## ⚙️ 실행 방법

### 1. 환경 설정
```bash
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 TMDB_API_KEY 입력
```

### 2. 데이터 수집 & 전처리 (선택 — 데이터 파일 있으면 생략)
```bash
cd scripts
python collect_data.py   # TMDB API로 영화 수집
python preprocess.py     # 전처리 및 태그 생성
python recommend.py      # 추천 모델 빌드 (pkl 파일 생성)
```

### 3. 서버 실행
```bash
uvicorn app.main:app --reload
```

브라우저에서 `http://localhost:8000/docs` 접속 → Swagger UI로 API 테스트

## 📡 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 헬스 체크 |
| GET | `/movies/popular?limit=20` | 평점순 인기 영화 목록 |
| GET | `/movies/search?q={검색어}` | 영화 제목 검색 |
| GET | `/movies/{movie_id}` | 영화 상세 정보 (감독, 출연진 포함) |
| GET | `/recommend?title={제목}&top_n=10` | 콘텐츠 기반 유사 영화 추천 |

### 추천 예시
```
GET /recommend?title=Inception&top_n=5
```
```json
{
  "query_title": "Inception",
  "recommendations": [
    { "title": "Interstellar", "similarity": 0.412, "vote_average": 8.4, ... },
    ...
  ]
}
```

## 🔍 추천 알고리즘

영화의 **장르, 감독, 주연 배우, 키워드, 줄거리**를 하나의 태그 문자열로 합쳐 TF-IDF로 벡터화하고, 코사인 유사도로 가장 비슷한 영화를 찾습니다.

```
tags = 장르 + 감독 + 출연진(3명) + 키워드(5개) + 줄거리(200자)
→ TF-IDF 벡터화 (max_features=5000)
→ 코사인 유사도 행렬 계산
→ 유사도 높은 순으로 TOP N 반환
```
