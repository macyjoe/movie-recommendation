const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : 'https://your-app.railway.app';  // 배포 후 Railway URL로 교체
const POSTER_BASE = 'https://image.tmdb.org/t/p/w300';

let prevSection = 'home';

// ── 유틸 ──────────────────────────────────────────────

function showLoading(msg = '불러오는 중...') {
  const el = document.getElementById('loading');
  el.innerHTML = `<div class="spinner"></div><p>${msg}</p>`;
  el.classList.remove('hidden');
}
function hideLoading() { document.getElementById('loading').classList.add('hidden'); }

function showSection(id) {
  ['home-section', 'search-section', 'recommend-section'].forEach(s => {
    document.getElementById(s).classList.add('hidden');
  });
  document.getElementById(id).classList.remove('hidden');
}

function showHome() {
  document.getElementById('search-input').value = '';
  showSection('home-section');
  prevSection = 'home';
}

function goBack() {
  showSection(prevSection === 'search' ? 'search-section' : 'home-section');
}

async function apiFetch(path) {
  const res = await fetch(API + path);
  if (!res.ok) throw new Error(`API 오류: ${res.status}`);
  return res.json();
}

function posterImg(posterPath, cls = '') {
  if (posterPath) {
    return `<img src="${POSTER_BASE}${posterPath}" alt="포스터" class="${cls}" loading="lazy"
      onerror="this.outerHTML='<div class=\\'no-poster${cls ? '-' + cls.replace('no-poster-','') : ''}\\'>🎬</div>'" />`;
  }
  return `<div class="no-poster${cls ? ' ' + cls : ''}">🎬</div>`;
}

// ── 카드 렌더 ─────────────────────────────────────────

function movieCard(movie, similarity = null) {
  const genres = Array.isArray(movie.genres) ? movie.genres.slice(0, 2) : [];
  const year = movie.release_date ? movie.release_date.slice(0, 4) : '';
  const badge = similarity !== null
    ? `<span class="similarity-badge">${(similarity * 100).toFixed(0)}% 일치</span>` : '';
  const genrePills = genres.map(g => `<span class="genre-pill">${g}</span>`).join('');

  return `
    <div class="movie-card" onclick="openModal(${movie.id})">
      <div class="poster-wrap">
        ${badge}
        ${posterImg(movie.poster_path)}
        <div class="card-overlay"></div>
      </div>
      <div class="card-info">
        <div class="card-title">${movie.title}</div>
        ${genrePills ? `<div class="card-genres">${genrePills}</div>` : ''}
        <div class="card-bottom">
          <div class="rating-badge">
            <svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            ${movie.vote_average.toFixed(1)}
          </div>
          ${year ? `<span class="year-text">${year}</span>` : ''}
        </div>
      </div>
    </div>`;
}

// ── 인기 영화 로드 ────────────────────────────────────

async function loadPopular() {
  showLoading();
  try {
    const movies = await apiFetch('/movies/popular?limit=20');
    const grid = document.getElementById('popular-grid');
    grid.innerHTML = movies.map(m => movieCard(m)).join('');
  } catch (e) {
    document.getElementById('popular-grid').innerHTML =
      `<div class="error-banner">⚠️ 서버에 연결할 수 없어요. FastAPI 서버가 실행 중인지 확인하세요.<br><code style="font-size:0.8rem;opacity:0.7">uvicorn app.main:app --reload</code></div>`;
  } finally {
    hideLoading();
  }
}

// ── 검색 ─────────────────────────────────────────────

async function handleSearch(e) {
  e.preventDefault();
  const query = document.getElementById('search-input').value.trim();
  if (!query) return;

  showLoading();
  prevSection = 'search';
  try {
    const movies = await apiFetch(`/movies/search?q=${encodeURIComponent(query)}&limit=20`);
    document.getElementById('search-heading').textContent = `"${query}" 검색 결과 (${movies.length}편)`;
    document.getElementById('search-grid').innerHTML = movies.map(m => movieCard(m)).join('');
    showSection('search-section');
  } catch (e) {
    document.getElementById('search-heading').textContent = `"${query}" 검색 결과`;
    document.getElementById('search-grid').innerHTML =
      `<div class="empty-state"><div class="icon">🔍</div><p>검색 결과가 없어요.</p></div>`;
    showSection('search-section');
  } finally {
    hideLoading();
  }
}

// ── 모달 ─────────────────────────────────────────────

async function openModal(movieId) {
  showLoading();
  try {
    const m = await apiFetch(`/movies/${movieId}`);
    const genres = Array.isArray(m.genres) ? m.genres : [];
    const directors = Array.isArray(m.directors) ? m.directors : [];
    const cast = Array.isArray(m.cast) ? m.cast.slice(0, 5) : [];
    const year = m.release_date ? m.release_date.slice(0, 4) : '';

    document.getElementById('modal-content').innerHTML = `
      <div class="modal-inner">
        ${posterImg(m.poster_path, 'no-poster-md')}
        <div>
          <div class="modal-title">${m.title}</div>
          <div class="modal-meta">
            <span class="tag rating">★ ${m.vote_average.toFixed(1)}</span>
            ${year ? `<span class="tag">${year}</span>` : ''}
            ${genres.map(g => `<span class="tag genre">${g}</span>`).join('')}
          </div>
          ${directors.length ? `<div style="font-size:0.82rem;color:#888;margin-bottom:6px">감독: ${directors.join(', ')}</div>` : ''}
          ${cast.length ? `<div style="font-size:0.82rem;color:#888">출연: ${cast.join(', ')}</div>` : ''}
        </div>
      </div>
      ${m.overview ? `<p class="modal-overview">${m.overview}</p>` : ''}
      <button class="recommend-btn" onclick="loadRecommend('${m.title.replace(/'/g, "\\'")}', ${m.id}, '${(m.poster_path||'').replace(/'/g,"\\'")}')">
        🎯 이 영화와 비슷한 영화 추천받기
      </button>`;

    document.getElementById('modal-overlay').classList.remove('hidden');
  } catch(e) {
    console.error(e);
  } finally {
    hideLoading();
  }
}

function closeModal(e) {
  if (!e || e.target === document.getElementById('modal-overlay') || e.currentTarget.classList.contains('modal-close')) {
    document.getElementById('modal-overlay').classList.add('hidden');
  }
}

// ── 추천 ─────────────────────────────────────────────

async function loadRecommend(title, movieId, posterPath) {
  closeModal();
  showLoading();
  try {
    const data = await apiFetch(`/recommend?title=${encodeURIComponent(title)}&top_n=12`);
    const detail = await apiFetch(`/movies/${movieId}`);

    // 선택한 영화 카드
    const genres = Array.isArray(detail.genres) ? detail.genres.slice(0,3).join(' · ') : '';
    document.getElementById('selected-movie-card').innerHTML = `
      <div class="selected-card">
        ${posterImg(detail.poster_path, 'no-poster-lg')}
        <div class="selected-info">
          <h3>${detail.title}</h3>
          <p style="color:#f5c518;margin-bottom:6px">★ ${detail.vote_average.toFixed(1)}&nbsp;&nbsp;${genres}</p>
          <p>${detail.overview ? detail.overview.slice(0, 150) + '...' : '줄거리 정보 없음'}</p>
        </div>
      </div>`;

    // 추천 목록
    const recs = data.recommendations;
    document.getElementById('recommend-grid').innerHTML = recs.length
      ? recs.map(m => movieCard(m, m.similarity)).join('')
      : `<div class="empty-state"><div class="icon">😢</div><p>추천 결과가 없어요.</p></div>`;

    showSection('recommend-section');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch(e) {
    console.error(e);
  } finally {
    hideLoading();
  }
}

// ── 초기화 ────────────────────────────────────────────
loadPopular();
