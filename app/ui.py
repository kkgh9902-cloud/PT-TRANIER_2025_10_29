# app/ui.py — 세션/공통 UI
import streamlit as st
from .constants import GOALS, GENDERS

def ensure_session_defaults():
    if "logged_in"   not in st.session_state: st.session_state.logged_in = False
    if "nickname"    not in st.session_state: st.session_state.nickname  = ""
    if "goal"        not in st.session_state: st.session_state.goal      = GOALS[0]
    if "gender"      not in st.session_state: st.session_state.gender    = GENDERS[0]
    if "plan"        not in st.session_state: st.session_state.plan      = []
    if "page"        not in st.session_state: st.session_state.page      = "🏋️ 운동 추천"
    if "popup_open"  not in st.session_state: st.session_state.popup_open = False
    if "popup_date"  not in st.session_state: st.session_state.popup_date = None

def render_login():
    from .storage import upsert_profile
    st.title("💪 헬스장 미아를 위한 PT쌤")
    st.subheader("로그인")
    with st.form("login_form"):
        nickname = st.text_input("닉네임")
        gender   = st.selectbox("성별", GENDERS)
        height   = st.number_input("키(cm)", min_value=0, max_value=300, value=170, step=1)
        weight   = st.number_input("몸무게(kg)", min_value=0, max_value=400, value=70, step=1)
        age      = st.number_input("나이", min_value=0, max_value=120, value=25, step=1)
        goal     = st.selectbox("운동 목표", GOALS)
        submit   = st.form_submit_button("로그인")
        if submit:
            if nickname.strip()=="":
                st.warning("닉네임을 입력하세요.")
            else:
                st.session_state.logged_in = True
                st.session_state.nickname  = nickname.strip()
                st.session_state.gender    = gender
                st.session_state.goal      = goal
                st.session_state.page      = "🏋️ 운동 추천"
                upsert_profile(nickname.strip(), gender, height, weight, age, goal)
                st.rerun()
    st.stop()

def render_sidebar_and_topbar():
    st.sidebar.header("사용자")
    st.sidebar.success(f"👤 {st.session_state.nickname}")
    menu_order = ["🏋️ 운동 추천", "🍽️ 식단 기록", "🗓️ 스케줄러", "👤 마이페이지"]
    menu = st.sidebar.radio("메뉴 선택", menu_order, index=menu_order.index(st.session_state.page))
    if menu != st.session_state.page:
        st.session_state.page = menu; st.rerun()
    left, _ = st.columns([4,1])
    with left:
        st.title("PT쌤")
        st.caption("PT쌤과 함께 헬스장 미아 탈출!")