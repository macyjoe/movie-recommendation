# 🎬 영화 추천 웹서비스

콘텐츠 기반 필터링을 활용한 영화 추천 웹서비스입니다.

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| 데이터 수집 | TMDB API, Python |
| 추천 알고리즘 | 콘텐츠 기반 필터링 (scikit-learn) |
| 백엔드 | FastAPI |
| 프론트엔드 | React |
| 배포 | AWS EC2 |

## 📁 프로젝트 구조

```
movie-recommendation/
├── data/           # 수집한 영화 데이터
├── scripts/        # 데이터 수집 및 전처리
├── backend/        # FastAPI 서버
├── frontend/       # React 앱
└── requirements.txt
```

## 🚀 진행 단계

- [x] 프로젝트 초기 세팅
- [x] TMDB API 연동 및 데이터 수집
- [ ] 데이터 전처리
- [ ] 추천 알고리즘 개발
- [ ] 백엔드 API 개발
- [ ] 프론트엔드 개발
- [ ] AWS 배포
