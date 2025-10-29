# app/pages/meals.py
import streamlit as st
from datetime import date
from ..constants import MEAL_TYPES
from ..storage import append_meal_row, fetch_meals_by_date, replace_meals_for_date

def render_meal_page():
    st.subheader("🍽️ 식단 기록 입력")
    c1, c2 = st.columns(2)
    with c1:
        d         = st.date_input("기록할 날짜", value=date.today())
        meal_type = st.selectbox("식사분류", MEAL_TYPES)
        menu_name = st.text_input("메뉴명")
        main_comp = st.text_input("주성분")
    with c2:
        grams = st.number_input("중량(g)", 0, 5000, 0, step=10)
        count = st.number_input("개수", 0, 50, 0, step=1)
        times = st.number_input("횟수", 0, 10, 0, step=1)

    if st.button("➕ 식단 추가"):
        if menu_name.strip()=="":
            st.warning("메뉴명을 입력하세요.")
        else:
            append_meal_row([
                d.strftime("%Y-%m-%d"), st.session_state.nickname, meal_type,
                menu_name.strip(), main_comp.strip(), int(grams), int(count), int(times)
            ])
            st.success("식단을 추가했습니다.")

    st.markdown("---")
    st.write("### ✏️ 오늘의 식단 미리보기 · 편집")
    today_date = date.today()
    todays = fetch_meals_by_date(st.session_state.nickname, today_date)

    if not todays:
        st.info("오늘 등록된 식단이 없습니다."); return

    editable_meals_today = [{
        "meal_type": it["meal_type"], "menu": it["menu"], "main": it["main"],
        "grams": it["grams"], "count": it["count"], "times": it["times"]
    } for it in todays]

    meal_sel_today = []
    for i, it in enumerate(editable_meals_today):
        with st.expander(f"{i+1}. [{it['meal_type']}] {it['menu']}"):
            r1, r2, r3 = st.columns([1,2,2])
            if r1.checkbox("선택", key=f"today_meal_sel_{i}"): meal_sel_today.append(i)
            it["meal_type"] = r2.selectbox("식사분류", MEAL_TYPES, index=MEAL_TYPES.index(it["meal_type"]) if it["meal_type"] in MEAL_TYPES else 0, key=f"today_meal_type_{i}")
            it["menu"]      = r3.text_input("메뉴명", it["menu"], key=f"today_meal_menu_{i}")
            c1, c2, c3 = st.columns(3)
            it["main"]  = c1.text_input("주성분", it["main"], key=f"today_meal_main_{i}")
            it["grams"] = c2.number_input("중량(g)", 0, 5000, it["grams"], step=10, key=f"today_meal_g_{i}")
            it["count"] = c3.number_input("개수", 0, 50, it["count"], step=1, key=f"today_meal_cnt_{i}")
            d1, _ = st.columns([1,6])
            it["times"] = d1.number_input("횟수", 0, 10, it["times"], step=1, key=f"today_meal_times_{i}")

    m_left, m_right, m_save = st.columns([1,1,2])
    if m_left.button("🗑️ 선택 삭제(오늘)"):
        for idx in sorted(meal_sel_today, reverse=True): del editable_meals_today[idx]
        replace_meals_for_date(st.session_state.nickname, today_date, editable_meals_today)
        st.success("선택한 오늘 식단을 삭제했습니다."); st.rerun()
    if m_right.button("🗑️ 전체 삭제(오늘)"):
        replace_meals_for_date(st.session_state.nickname, today_date, [])
        st.success("오늘 식단을 모두 삭제했습니다."); st.rerun()
    if m_save.button("💾 오늘 식단 편집 저장"):
        replace_meals_for_date(st.session_state.nickname, today_date, editable_meals_today)
        st.success("오늘 식단 편집 내용을 저장했습니다."); st.rerun()