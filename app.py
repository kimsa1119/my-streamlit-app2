import streamlit as st

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬", layout="centered")

st.title("🎬 나와 어울리는 영화는?")
st.write("간단한 질문 5개로 당신의 영화 취향/무드를 가볍게 알아보는 심리테스트예요. 아래 질문에 답하고 결과를 확인해보세요!")

st.divider()

# 1
q1 = st.radio(
    "1. 주말에 가장 하고 싶은 것은?",
    ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"],
    key="q1"
)

# 2
q2 = st.radio(
    "2. 스트레스 받으면?",
    ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"],
    key="q2"
)

# 3
q3 = st.radio(
    "3. 영화에서 중요한 것은?",
    ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"],
    key="q3"
)

# 4
q4 = st.radio(
    "4. 여행 스타일?",
    ["계획적", "즉흥적", "액티비티", "힐링"],
    key="q4"
)

# 5
q5 = st.radio(
    "5. 친구 사이에서 나는?",
    ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"],
    key="q5"
)

st.divider()

if st.button("결과 보기", type="primary"):
    # (다음 시간에 API 연동/분석 로직 추가 예정)
    st.info("분석 중...")

import streamlit as st
import requests

st.title("🎬 TMDB API 테스트")

# 사이드바에서 API 키 입력
TMDB_API_KEY = st.sidebar.text_input("TMDB API Key", type="password")

if TMDB_API_KEY:
    if st.button("인기 영화 가져오기"):
        # TMDB에서 인기 영화 가져오기
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=ko-KR"
        response = requests.get(url)
        data = response.json()
        
        # 첫 번째 영화 정보 출력
        movie = data['results'][0]
        st.write(f"🎬 제목: {movie['title']}")
        st.write(f"⭐ 평점: {movie['vote_average']}/10")
        st.write(f"📅 개봉일: {movie['release_date']}")
        st.write(f"📝 줄거리: {movie['overview'][:100]}...")
else:
    st.info("사이드바에 TMDB API Key를 입력해주세요.")

