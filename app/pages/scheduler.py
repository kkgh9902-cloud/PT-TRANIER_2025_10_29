# app/pages/scheduler.py
import streamlit as st
import calendar
from datetime import date
from ..storage import fetch_logs_month, fetch_meals_by_date, replace_meals_for_date, replace_logs_for_date
from ..constants import GOALS, SPLITS, MEAL_TYPES

def render_scheduler_page():
    st.subheader("🗓️ Monthly 운동 기록")
    left, right = st.columns(2)
    with left:
        today = date.today()
        picked = st.date_input("조회할 월 선택", value=date(today.year, today.month, 1), key="picked_month")
        y, m = picked.year, picked.month
    with right:
        nick_filter = st.text_input("닉네임 필터(빈칸이면 전체)", value=st.session_state.nickname, key="nick_filter")
    logs = fetch_logs_month(nick_filter, y, m)

    daily = {}
    for lg in logs:
        d_ = lg["date"]
        if d_ not in daily: daily[d_] = {"volume":0, "done_sets":0, "items":[]}
        daily[d_]["volume"] += int(lg.get("volume",0) or 0)
        daily[d_]["done_sets"] += int(lg.get("done_sets",0) or 0)
        daily[d_]["items"].append(lg)

    st.markdown("---")
    st.write(f"**{y}년 {m}월** (각 날짜: 완료세트) — 일자 클릭 시 상세 편집 팝업 열림")

    cal = calendar.Calendar(firstweekday=0)
    for wk in cal.monthdatescalendar(y, m):
        cols = st.columns(7)
        for i, d_ in enumerate(wk):
            box = cols[i]
            if d_.month == m:
                label = f"{d_.day}"
                if d_ in daily: label += f"\n세트:{daily[d_]['done_sets']}"
                if box.button(label, key=f"day_{d_.isoformat()}"):
                    st.session_state.popup_open = True
                    st.session_state.popup_date = d_
                    st.rerun()
            else:
                box.write("")
    st.markdown("---")

    if st.session_state.popup_open and st.session_state.popup_date:
        _render_day_popup(logs)

def _render_day_popup(logs):
    d = st.session_state.popup_date
    st.info(f"📌 **{d} 상세 기록 편집** — 편집 후 꼭 저장하세요!")
    day_logs  = [x for x in logs if x["date"] == d]
    day_meals = fetch_meals_by_date(st.session_state.nickname, d)

    # 운동 기록
    st.subheader(f"🏋️ {d} 운동 기록")
    if not day_logs:
        st.write("휴식!")
        editable_logs = []
    else:
        editable_logs = [{
            "goal": it["goal"], "split": it["split"], "part": it["part"], "name": it["name"],
            "sets": it["sets"], "reps": it["reps"], "weight": it["weight"],
            "done_sets": it["done_sets"], "volume": it["volume"]
        } for it in day_logs]

        del_sel = []
        for i, it in enumerate(editable_logs):
            with st.expander(f"{i+1}. [{it['part']}] {it['name']}"):
                r1, r2, r3, r4, r5, r6 = st.columns([1,1,1,1,1,1])
                if r1.checkbox("선택", key=f"log_sel_{i}"): del_sel.append(i)
                it["part"]   = r2.text_input("부위", it["part"], key=f"log_part_{i}")
                it["name"]   = r3.text_input("운동명", it["name"], key=f"log_name_{i}")
                it["sets"]   = r4.number_input("세트", 1, 10, it["sets"], key=f"log_sets_{i}")
                it["reps"]   = r5.number_input("반복", 1, 50, it["reps"], key=f"log_reps_{i}")
                it["weight"] = r6.number_input("무게(kg)", 0, 500, it["weight"], step=5, key=f"log_w_{i}")

                c1, c2, c3 = st.columns(3)
                key_done = f"log_done_{i}"
                max_sets = max(0, int(it.get("sets") or 0))
                if key_done in st.session_state:
                    try: st.session_state[key_done] = int(st.session_state[key_done] or 0)
                    except Exception: st.session_state[key_done] = 0
                    st.session_state[key_done] = min(max(0, st.session_state[key_done]), max_sets)
                default_done = int(it.get("done_sets") or st.session_state.get(key_done, 0) or 0)
                default_done = min(max(0, default_done), max_sets)

                it["done_sets"] = c1.number_input("완료세트", 0, max_sets, default_done, step=1, key=key_done)
                it["goal"]  = c2.selectbox("목표", GOALS, index=GOALS.index(it["goal"]) if it["goal"] in GOALS else 0, key=f"log_goal_{i}")
                it["split"] = c3.selectbox("분할", SPLITS, index=SPLITS.index(it["split"]) if it["split"] in SPLITS else 0, key=f"log_split_{i}")

                m1, m2, _ = st.columns([1,1,5])
                if m1.button("⬆ 위로", key=f"log_up_{i}") and i>0:
                    editable_logs[i-1], editable_logs[i] = editable_logs[i], editable_logs[i-1]; st.rerun()
                if m2.button("⬇ 아래로", key=f"log_dn_{i}") and i<len(editable_logs)-1:
                    editable_logs[i+1], editable_logs[i] = editable_logs[i], editable_logs[i+1]; st.rerun()

        c_left, c_right = st.columns([1,1])
        if c_left.button("🗑️ 선택 삭제"):
            for idx in sorted(del_sel, reverse=True): del editable_logs[idx]
            st.success("선택 항목을 삭제했습니다.")
            replace_logs_for_date(st.session_state.nickname, d, editable_logs); st.rerun()
        if c_right.button("🗑️ 전체 삭제"):
            replace_logs_for_date(st.session_state.nickname, d, []); st.success("해당 날짜의 운동 기록을 모두 삭제했습니다."); st.rerun()

        if st.button("💾 운동 기록 저장"):
            for it in editable_logs:
                it["volume"] = int(it["weight"]) * int(it["reps"]) * int(it["done_sets"])
            replace_logs_for_date(st.session_state.nickname, d, editable_logs)
            st.success("운동 기록을 저장했습니다."); st.rerun()

    st.markdown("---")

    # 식단 기록
    st.subheader("🍽️ 식단 기록(편집)")
    if not day_meals:
        st.write("기록 없음")
    else:
        editable_meals = [{
            "meal_type": it["meal_type"], "menu": it["menu"], "main": it["main"],
            "grams": it["grams"], "count": it["count"], "times": it["times"]
        } for it in day_meals]

        meal_sel = []
        for i, it in enumerate(editable_meals):
            with st.expander(f"{i+1}. [{it['meal_type']}] {it['menu']}"):
                r1, r2, r3 = st.columns([1,2,2])
                if r1.checkbox("선택", key=f"meal_sel_{i}"): meal_sel.append(i)
                it["meal_type"] = r2.selectbox("식사분류", MEAL_TYPES, index=MEAL_TYPES.index(it["meal_type"]) if it["meal_type"] in MEAL_TYPES else 0, key=f"meal_type_{i}")
                it["menu"] = r3.text_input("메뉴명", it["menu"], key=f"meal_menu_{i}")
                c1, c2, c3 = st.columns(3)
                it["main"]  = c1.text_input("주성분", it["main"], key=f"meal_main_{i}")
                it["grams"] = c2.number_input("중량(g)", 0, 5000, it["grams"], step=10, key=f"meal_g_{i}")
                it["count"] = c3.number_input("개수", 0, 50, it["count"], step=1, key=f"meal_cnt_{i}")
                d1, _ = st.columns([1,6])
                it["times"] = d1.number_input("횟수", 0, 10, it["times"], step=1, key=f"meal_times_{i}")

        m_left, m_right = st.columns([1,1])
        if m_left.button("🗑️ 선택 삭제(식단)"):
            for idx in sorted(meal_sel, reverse=True): del editable_meals[idx]
            replace_meals_for_date(st.session_state.nickname, d, editable_meals)
            st.success("선택 식단을 삭제했습니다."); st.rerun()
        if m_right.button("🗑️ 전체 삭제(식단)"):
            replace_meals_for_date(st.session_state.nickname, d, [])
            st.success("식단 기록을 모두 삭제했습니다."); st.rerun()

        if st.button("💾 식단 기록 저장"):
            replace_meals_for_date(st.session_state.nickname, d, editable_meals)
            st.success("식단 기록을 저장했습니다."); st.rerun()

    if st.button("닫기"):
        st.session_state.popup_open = False
        st.session_state.popup_date = None
        st.rerun()