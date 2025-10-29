# app/pages/mypage.py
import streamlit as st
from ..constants import GOALS, GENDERS
from ..storage import load_profile, upsert_profile

def render_mypage():
    st.subheader("👤 마이페이지 — 내 정보 수정")
    current = load_profile(st.session_state.nickname) or {
        "nickname": st.session_state.nickname, "gender": st.session_state.gender,
        "height": 170, "weight": 70, "age": 25, "goal": st.session_state.goal
    }
    with st.form("edit_form"):
        new_nick   = st.text_input("닉네임", value=current["nickname"])
        new_gender = st.selectbox("성별", GENDERS, index=GENDERS.index(current.get("gender", GENDERS[0])))
        new_height = st.number_input("키(cm)", 0, 300, int(current.get("height") or 170))
        new_weight = st.number_input("몸무게(kg)", 0, 400, int(current.get("weight") or 70))
        new_age    = st.number_input("나이", 0, 120, int(current.get("age") or 25))
        new_goal   = st.selectbox("운동 목표", GOALS, index=GOALS.index(current.get("goal", GOALS[0])))
        save       = st.form_submit_button("저장")
        if save:
            if new_nick.strip()=="":
                st.warning("닉네임은 비워둘 수 없습니다.")
            else:
                upsert_profile(new_nick.strip(), new_gender, new_height, new_weight, new_age, new_goal)
                st.session_state.nickname = new_nick.strip()
                st.session_state.gender   = new_gender
                st.session_state.goal     = new_goal
                st.success("수정 완료!"); st.rerun()

    st.markdown("---")
    spacer1, spacer2 = st.columns([6,1])
    with spacer2:
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.plan = []
            st.rerun()