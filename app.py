import streamlit as st
import tmdbsimple as tmdb
from collections import defaultdict
from typing import Dict, List, Tuple, Any

st.set_page_config(page_title="🎬 나와 어울리는 영화는?", page_icon="🎬", layout="centered")


# =========================
# TMDB 장르 ID
# =========================
GENRES = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}


# =========================
# 분석 로직 (답변 -> 장르 점수)
# =========================
def analyze_answers_top2(answers: Dict[str, str]) -> Tuple[List[Tuple[str, int]], Dict[str, List[str]]]:
    """
    반환:
      - top2: [("드라마", 9), ("로맨스", 7)] 같이 점수 높은 순 2개
      - reasons: {"드라마": ["...","..."], ...} 장르별 추천 근거 문장 목록
    """
    score = defaultdict(int)
    reasons = defaultdict(list)

    def add(genre: str, pts: int, reason: str):
        score[genre] += pts
        reasons[genre].append(reason)

    # 1. 주말
    a = answers["q1"]
    if a == "집에서 휴식":
        add("드라마", 2, "주말엔 조용히 쉬는 선택 → 잔잔한 감정선(드라마)에 강하게 끌릴 확률이 높아요.")
        add("로맨스", 1, "편안한 분위기를 선호 → 관계 중심(로맨스)도 잘 맞을 수 있어요.")
    elif a == "친구와 놀기":
        add("코미디", 2, "친구와 노는 선택 → 가벼운 웃음 포인트(코미디)를 좋아할 가능성이 커요.")
        add("로맨스", 1, "사람 사이 케미를 즐길 수 있어 → 로맨스에도 플러스!")
    elif a == "새로운 곳 탐험":
        add("액션", 2, "탐험/새로움 선호 → 어드벤처 무드(액션)에 점수!")
        add("판타지", 1, "새로운 세계를 좋아한다면 → 판타지도 잘 맞아요.")
    elif a == "혼자 취미생활":
        add("SF", 2, "혼자 몰입하는 선택 → 세계관 몰입형(SF)과 궁합이 좋아요.")
        add("판타지", 1, "상상력을 쓰는 취미라면 → 판타지도 가능성!")

    # 2. 스트레스
    a = answers["q2"]
    if a == "혼자 있기":
        add("드라마", 2, "혼자 정리 → 감정 이입형(드라마) 선호 경향")
        add("SF", 1, "혼자 몰입 → SF/판타지 몰입도 가능")
    elif a == "수다 떨기":
        add("코미디", 2, "수다로 해소 → 코미디 텐션과 맞아요.")
        add("로맨스", 1, "관계/대화 중심 서사(로맨스)도 잘 맞을 수 있어요.")
    elif a == "운동하기":
        add("액션", 2, "운동으로 해소 → 액션/스릴 선호 경향")
        add("SF", 1, "스케일 큰 장면 선호로 SF도 가능")
    elif a == "맛있는 거 먹기":
        add("코미디", 2, "소확행 스타일 → 부담 없이 웃는 코미디와 찰떡")
        add("드라마", 1, "따뜻한 감성 드라마도 가능")

    # 3. 영화에서 중요한 것
    a = answers["q3"]
    if a == "감동 스토리":
        add("드라마", 3, "스토리/감동 최우선 → 드라마 적중!")
        add("로맨스", 1, "감정선 중요 → 로맨스도 플러스")
    elif a == "시각적 영상미":
        add("SF", 3, "비주얼 중시 → SF(스케일/연출) 최적")
        add("판타지", 2, "화려한 세계관 → 판타지 적합")
    elif a == "깊은 메시지":
        add("SF", 2, "‘만약에?’ 질문 → SF의 강점")
        add("드라마", 2, "현실/인간에 대한 질문 → 드라마 강점")
    elif a == "웃는 재미":
        add("코미디", 3, "웃음이 최우선 → 코미디 확정급!")

    # 4. 여행 스타일
    a = answers["q4"]
    if a == "계획적":
        add("드라마", 1, "흐름/구조 선호 → 서사 탄탄한 드라마")
        add("SF", 1, "논리적 세계관 → SF도 가능")
    elif a == "즉흥적":
        add("액션", 1, "즉흥성 → 어드벤처 무드(액션)")
        add("로맨스", 1, "예상치 못한 전개 → 로맨스")
        add("코미디", 1, "해프닝 → 코미디")
    elif a == "액티비티":
        add("액션", 3, "활동성 최고 → 액션에 크게 가산")
    elif a == "힐링":
        add("드라마", 2, "힐링 선호 → 드라마")
        add("로맨스", 2, "설렘/따뜻함 → 로맨스")

    # 5. 친구 사이에서
    a = answers["q5"]
    if a == "듣는 역할":
        add("드라마", 2, "공감/경청 → 감정선 드라마에 강함")
        add("로맨스", 1, "관계 감각 → 로맨스도 적합")
    elif a == "주도하기":
        add("액션", 2, "리드 성향 → 액션 주인공 타입")
        add("SF", 1, "전략/판단 무드 → SF도 가능")
    elif a == "분위기 메이커":
        add("코미디", 2, "분위기 담당 → 코미디")
        add("로맨스", 1, "케미/텐션 → 로맨스도 가능")
    elif a == "필요할 때 나타남":
        add("SF", 2, "한방 임팩트 → SF/특이한 매력")
        add("판타지", 2, "신비한 키플레이어 → 판타지")

    ranked = sorted(score.items(), key=lambda x: x[1], reverse=True)
    top2 = ranked[:2] if len(ranked) >= 2 else ranked

    # 안전장치: 점수 아예 없을 경우
    if not top2:
        top2 = [("드라마", 1)]

    return top2, dict(reasons)


# =========================
# TMDB 호출 유틸
# =========================
@st.cache_data(show_spinner=False, ttl=60 * 60)
def tmdb_get_config(api_key: str) -> Dict[str, Any]:
    tmdb.API_KEY = api_key
    cfg = tmdb.Configuration().info()
    return cfg

def build_poster_url(cfg: Dict[str, Any], poster_path: str) -> str:
    if not poster_path:
        return ""
    images = cfg.get("images", {}) if cfg else {}
    base_url = images.get("secure_base_url") or images.get("base_url") or "https://image.tmdb.org/t/p/"
    sizes = images.get("poster_sizes") or []
    # 선호 사이즈: w500 > w342 > original
    preferred = "w500" if "w500" in sizes else ("w342" if "w342" in sizes else (sizes[-1] if sizes else "w500"))
    return f"{base_url}{preferred}{poster_path}"

@st.cache_data(show_spinner=False, ttl=60 * 30)
def discover_by_genre(api_key: str, genre_id: int, language: str = "ko-KR", page: int = 1) -> List[Dict[str, Any]]:
    tmdb.API_KEY = api_key
    d = tmdb.Discover()
    # discover/movie 파라미터: sort_by, with_genres 등
    # (tmdbsimple은 키워드 인자로 넘기면 querystring으로 처리)
    res = d.movie(
        with_genres=str(genre_id),
        language=language,
        sort_by="popularity.desc",
        include_adult="false",
        page=page
    )
    return (res.get("results") or [])

@st.cache_data(show_spinner=False, ttl=60 * 60)
def movie_detail_with_extras(api_key: str, movie_id: int, language: str = "ko-KR") -> Dict[str, Any]:
    tmdb.API_KEY = api_key
    m = tmdb.Movies(movie_id)
    # append_to_response로 videos, credits 같이 받기
    return m.info(language=language, append_to_response="videos,credits")

def pick_trailer_url(detail: Dict[str, Any]) -> str:
    videos = (detail.get("videos") or {}).get("results") or []
    # 유튜브 트레일러 우선
    for v in videos:
        if (v.get("site") == "YouTube") and (v.get("type") in ["Trailer", "Teaser"]) and v.get("key"):
            return f"https://www.youtube.com/watch?v={v['key']}"
    return ""

def top_cast_names(detail: Dict[str, Any], n: int = 3) -> str:
    cast = (detail.get("credits") or {}).get("cast") or []
    names = [c.get("name") for c in cast[:n] if c.get("name")]
    return ", ".join(names)


# =========================
# UI
# =========================
st.title("🎬 나와 어울리는 영화는?")
st.write("질문 5개에 답하면, 답변을 바탕으로 **가장 잘 맞는 장르(Top2)** 를 뽑고 TMDB에서 **인기 영화 5편**을 추천해드려요!")

st.sidebar.header("🔑 TMDB 설정")
api_key = st.sidebar.text_input("TMDB API Key", type="password", placeholder="여기에 API Key 입력")

st.sidebar.markdown("---")
st.sidebar.caption("※ TMDB 데이터/이미지를 사용합니다. (표기 문구는 앱 하단 참고)")


st.divider()

q1 = st.radio(
    "1. 주말에 가장 하고 싶은 것은?",
    ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"],
    key="q1"
)
q2 = st.radio(
    "2. 스트레스 받으면?",
    ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"],
    key="q2"
)
q3 = st.radio(
    "3. 영화에서 중요한 것은?",
    ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"],
    key="q3"
)
q4 = st.radio(
    "4. 여행 스타일?",
    ["계획적", "즉흥적", "액티비티", "힐링"],
    key="q4"
)
q5 = st.radio(
    "5. 친구 사이에서 나는?",
    ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"],
    key="q5"
)

st.divider()

if st.button("결과 보기", type="primary"):
    if not api_key.strip():
        st.error("사이드바에 TMDB API Key를 입력해 주세요!")
        st.stop()

    answers = {"q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5}

    with st.spinner("분석 중..."):
        top2, reasons_map = analyze_answers_top2(answers)

        # 이미지 설정(포스터 URL 하드코딩 제거)
        try:
            cfg = tmdb_get_config(api_key.strip())
        except Exception as e:
            st.error(f"TMDB 설정 정보를 가져오지 못했어요(API Key 확인 필요).\n\n에러: {e}")
            st.stop()

        # Top2 장르
        primary_genre, primary_score = top2[0]
        secondary_genre, secondary_score = (top2[1] if len(top2) > 1 else (None, 0))

        # 후보 수집: 장르당 20개씩 가져오고 합쳐서 재정렬
        candidates: Dict[int, Dict[str, Any]] = {}

        def add_candidates(genre_name: str, genre_id: int, pages: int = 1):
            for p in range(1, pages + 1):
                for item in discover_by_genre(api_key.strip(), genre_id, page=p):
                    mid = item.get("id")
                    if mid:
                        candidates[mid] = item

        add_candidates(primary_genre, GENRES[primary_genre], pages=1)
        if secondary_genre:
            add_candidates(secondary_genre, GENRES[secondary_genre], pages=1)

        # 내부 재랭킹: popularity + vote_average + (primary/secondary 장르 보너스)
        def rank_score(item: Dict[str, Any]) -> float:
            pop = float(item.get("popularity") or 0.0)
            vote = float(item.get("vote_average") or 0.0)
            gids = item.get("genre_ids") or []
            bonus = 0.0
            if GENRES[primary_genre] in gids:
                bonus += 8.0
            if secondary_genre and GENRES[secondary_genre] in gids:
                bonus += 4.0
            # vote는 0~10이라 스케일 맞추려고 *10 정도
            return pop * 0.6 + (vote * 10.0) * 0.4 + bonus

        ranked_movies = sorted(candidates.values(), key=rank_score, reverse=True)[:5]

    # =========================
    # 결과 표시
    # =========================
    st.subheader("🧠 분석 결과")
    if secondary_genre:
        st.write(f"당신의 Top 장르는 **{primary_genre}** (점수 {primary_score}), 다음은 **{secondary_genre}** (점수 {secondary_score})예요.")
    else:
        st.write(f"당신의 Top 장르는 **{primary_genre}** (점수 {primary_score})예요.")

    # 장르 추천 이유(상위 2개 문장만)
    primary_reason = " ".join((reasons_map.get(primary_genre) or [])[:2]) or "당신의 선택이 이 장르와 잘 맞아요."
    st.caption(f"추천 근거: {primary_reason}")

    st.subheader("🍿 추천 영화 5편")

    if not ranked_movies:
        st.warning("추천할 영화를 찾지 못했어요. 잠시 후 다시 시도해 주세요.")
        st.stop()

    for item in ranked_movies:
        movie_id = item.get("id")
        title = item.get("title") or "제목 없음"

        # 상세 정보(줄거리/출연/예고편) 고도화
        try:
            detail = movie_detail_with_extras(api_key.strip(), movie_id)
        except Exception:
            detail = item  # 실패 시 discover 결과로 fallback

        overview = detail.get("overview") or "줄거리 정보가 없어요."
        vote = float(detail.get("vote_average") or 0.0)
        poster_url = build_poster_url(cfg, detail.get("poster_path") or "")
        trailer = pick_trailer_url(detail)
        cast = top_cast_names(detail, n=3)

        # 영화별 추천 이유(간단 + 개인화)
        why = f"당신의 답변에서 **{primary_genre}** 성향이 가장 강했어요. 그래서 {primary_genre} 분위기의 인기작 중에서 골랐어요."
        if secondary_genre:
            why += f" (또한 **{secondary_genre}** 취향도 보여서 함께 고려했어요.)"

        with st.container(border=True):
            cols = st.columns([1, 2])
            with cols[0]:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.caption("포스터 없음")
            with cols[1]:
                st.markdown(f"### {title}")
                st.write(f"⭐ 평점: **{vote:.1f}**")
                if cast:
                    st.caption(f"주요 출연: {cast}")
                st.write(overview)

                if trailer:
                    st.link_button("예고편 보기 (YouTube)", trailer)

                st.caption(f"💡 이 영화를 추천하는 이유: {why}")

st.markdown("---")
# TMDB FAQ에 나온 표기 요구사항 반영 :contentReference[oaicite:2]{index=2}
st.caption('This product uses the TMDB API but is not endorsed or certified by TMDB.')

