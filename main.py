# main.py — Streamlit entrypoint
# 실행: streamlit run main.py

import streamlit as st
from datetime import date
from app.constants import GOALS, GENDERS
from app.storage import init_workbook, read_exercises_by_part
from app.ui import ensure_session_defaults, render_login, render_sidebar_and_topbar
from app.pages.workout import render_workout_page
from app.pages.meals import render_meal_page
from app.pages.scheduler import render_scheduler_page
from app.pages.mypage import render_mypage

st.set_page_config(page_title="PT쌤", page_icon="💪", layout="wide")

def main():
    # 스토리지 준비
    init_workbook()
    DB = read_exercises_by_part()

    # 세션 상태 기본값
    ensure_session_defaults()

    # 로그인 게이트
    if not st.session_state.logged_in:
        render_login()  # 내부에서 st.stop()
    
    # 공통 상단/사이드바
    render_sidebar_and_topbar()

    # 라우팅
    page = st.session_state.page
    if   page == "🏋️ 운동 추천": render_workout_page(DB)
    elif page == "🍽️ 식단 기록": render_meal_page()
    elif page == "🗓️ 스케줄러":   render_scheduler_page()
    elif page == "👤 마이페이지":  render_mypage()

if __name__ == "__main__":
    main()