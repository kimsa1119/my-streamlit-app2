import streamlit as st
import requests
from collections import defaultdict

st.set_page_config(page_title="🎬 나와 어울리는 영화는?", page_icon="🎬", layout="centered")

TMDB_BASE = "https://api.themoviedb.org/3"

GENRES = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}

# =========================
# TMDB API 유틸
# =========================
@st.cache_data(ttl=60 * 60)
def get_tmdb_config(api_key):
    url = f"{TMDB_BASE}/configuration"
    r = requests.get(url, params={"api_key": api_key}, timeout=10)
    r.raise_for_status()
    return r.json()

def build_poster_url(cfg, poster_path):
    if not poster_path:
        return ""
    base = cfg["images"]["secure_base_url"]
    size = "w500" if "w500" in cfg["images"]["poster_sizes"] else cfg["images"]["poster_sizes"][-1]
    return f"{base}{size}{poster_path}"

@st.cache_data(ttl=60 * 30)
def discover_movies(api_key, genre_id, page=1):
    url = f"{TMDB_BASE}/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "popularity.desc",
        "include_adult": False,
        "page": page,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("results", [])

@st.cache_data(ttl=60 * 60)
def movie_detail(api_key, movie_id):
    url = f"{TMDB_BASE}/movie/{movie_id}"
    params = {
        "api_key": api_key,
        "language": "ko-KR",
        "append_to_response": "videos,credits",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def pick_trailer(detail):
    videos = detail.get("videos", {}).get("results", [])
    for v in videos:
        if v.get("site") == "YouTube" and v.get("type") in ["Trailer", "Teaser"]:
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def top_cast(detail, n=3):
    cast = detail.get("credits", {}).get("cast", [])
    return ", ".join([c["name"] for c in cast[:n]])

# =========================
# 심리테스트 분석
# =========================
def analyze_answers(answers):
    score = defaultdict(int)
    reason = defaultdict(list)

    def add(g, p, r):
        score[g] += p
        reason[g].append(r)

    # Q1
    if answers["q1"] == "집에서 휴식":
        add("드라마", 2, "잔잔한 휴식을 선호")
        add("로맨스", 1, "감정 중심 이야기 선호")
    elif answers["q1"] == "친구와 놀기":
        add("코미디", 2, "사람들과 웃는 걸 좋아함")
    elif answers["q1"] == "새로운 곳 탐험":
        add("액션", 2, "모험/도전 성향")
    elif answers["q1"] == "혼자 취미생활":
        add("SF", 2, "혼자 몰입하는 타입")

    # Q2
    if answers["q2"] == "운동하기":
        add("액션", 2, "에너지 발산형")
    elif answers["q2"] == "수다 떨기":
        add("코미디", 2, "대화/웃음으로 해소")
    elif answers["q2"] == "혼자 있기":
        add("드라마", 2, "내면 정리형")

    # Q3
    if answers["q3"] == "감동 스토리":
        add("드라마", 3, "스토리 중시")
    elif answers["q3"] == "시각적 영상미":
        add("SF", 3, "비주얼 중시")
    elif answers["q3"] == "웃는 재미":
        add("코미디", 3, "웃음 중시")

    # Q4
    if answers["q4"] == "액티비티":
        add("액션", 3)
    elif answers["q4"] == "힐링":
        add("드라마", 2)

    # Q5
    if answers["q5"] == "분위기 메이커":
        add("코미디", 2)
    elif answers["q5"] == "주도하기":
        add("액션", 2)

    ranked = sorted(score.items(), key=lambda x: x[1], reverse=True)
    return ranked[0][0], reason[ranked[0][0]]

# =========================
# UI
# =========================
st.title("🎬 나와 어울리는 영화는?")
st.write("간단한 질문으로 당신에게 어울리는 영화 장르와 작품을 추천해드려요!")

st.sidebar.header("🔑 TMDB API Key")
api_key = st.sidebar.text_input("API Key", type="password")

st.divider()

q1 = st.radio("1. 주말에 가장 하고 싶은 것은?", ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"])
q2 = st.radio("2. 스트레스 받으면?", ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"])
q3 = st.radio("3. 영화에서 중요한 것은?", ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"])
q4 = st.radio("4. 여행 스타일?", ["계획적", "즉흥적", "액티비티", "힐링"])
q5 = st.radio("5. 친구 사이에서 나는?", ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"])

if st.button("결과 보기", type="primary"):
    if not api_key:
        st.error("TMDB API Key를 입력해주세요.")
        st.stop()

    with st.spinner("분석 중..."):
        cfg = get_tmdb_config(api_key)
        genre, reasons = analyze_answers({
            "q1": q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5
        })
        movies = discover_movies(api_key, GENRES[genre])[:5]

    st.subheader(f"🎯 추천 장르: {genre}")
    st.caption(" / ".join(reasons))

    for m in movies:
        detail = movie_detail(api_key, m["id"])
        poster = build_poster_url(cfg, detail.get("poster_path"))
        trailer = pick_trailer(detail)

        with st.container(border=True):
            cols = st.columns([1, 2])
            with cols[0]:
                if poster:
                    st.image(poster, use_container_width=True)
            with cols[1]:
                st.markdown(f"### {detail['title']}")
                st.write(f"⭐ 평점: {detail['vote_average']:.1f}")
                st.write(detail.get("overview", "줄거리 없음"))
                if trailer:
                    st.link_button("🎞 예고편 보기", trailer)
                st.caption("💡 이 영화를 추천하는 이유: 당신의 선택이 이 장르 성향과 잘 맞아요.")

st.markdown("---")
st.caption("This product uses the TMDB API but is not endorsed or certified by TMDB.")
