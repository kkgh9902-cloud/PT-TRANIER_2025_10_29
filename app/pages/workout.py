# app/pages/workout.py
import streamlit as st
from datetime import date
from ..constants import GOAL_PRESET, SPLITS
from ..domain import recommend_by_split
from ..storage import append_log_row

def render_workout_page(DB):
    st.subheader("🏋️ 오늘은 어떤 운동 계획인가요?")
    split = st.selectbox("운동 부위", SPLITS, key="split_main")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔮 선택한 부위별 운동 추천받기! "):
            st.session_state.plan = recommend_by_split(st.session_state.goal, split, DB)
            st.success("추천을 생성했습니다. 아래에서 편집 후 저장하세요.")
    with c2:
        st.write("**직접 추가**")
        part_pick  = st.selectbox("부위 선택", list(DB.keys()), key="part_pick")
        ex_choices = st.multiselect("운동 선택", DB.get(part_pick, []), key="ex_choices")
        add_sets   = st.number_input("세트 수", 1, 10, 3, key="add_sets")
        add_reps   = st.number_input("반복 수", 1, 50, 10, key="add_reps")
        add_weight = st.number_input("무게(kg)", 0, 500, 0, step=5, key="add_weight")
        if st.button("➕ 추가"):
            for ex in ex_choices:
                st.session_state.plan.append({
                    "part": part_pick, "name": ex,
                    "sets": int(add_sets), "reps": int(add_reps),
                    "intensity": GOAL_PRESET[st.session_state.goal]["intensity"],
                    "weight": int(add_weight)
                })
            st.success("계획에 추가했습니다.")

    st.markdown("---"); st.write("### 📝 내가 계획한 오늘의 운동")
    if not st.session_state.plan:
        st.info("추천 받거나 직접 추가해 보세요.")
        return

    delete_indices = []
    for idx, item in enumerate(st.session_state.plan):
        with st.expander(f"{idx+1}. [{item['part']}] {item['name']}"):
            c0, c1, c2, c3, c4 = st.columns([1,1,1,1,1])
            if c0.button("🗑️ 삭제", key=f"del_{idx}"): delete_indices.append(idx)
            item["sets"]   = c1.number_input("세트", 1, 10, int(item["sets"]), key=f"sets_{idx}")
            item["reps"]   = c2.number_input("반복", 1, 50, int(item["reps"]), key=f"reps_{idx}")
            item["weight"] = c3.number_input("무게(kg)", 0, 500, int(item["weight"]), step=5, key=f"w_{idx}")
            item["intensity"] = c4.selectbox(
                "강도", ["낮음","중간","높음"],
                index=["낮음","중간","높음"].index(item["intensity"]), key=f"int_{idx}"
            )

            key_done = f"done_{idx}"
            max_sets_cur = int(item.get("sets") or 0)
            if key_done in st.session_state:
                try: st.session_state[key_done] = int(st.session_state[key_done] or 0)
                except Exception: st.session_state[key_done] = 0
                st.session_state[key_done] = min(max(0, st.session_state[key_done]), max_sets_cur)
            default_done = int(item.get("done_sets", 0) or st.session_state.get(key_done, 0) or 0)
            default_done = min(max(0, default_done), max_sets_cur)
            done = st.slider("완료 세트 수", 0, max_sets_cur, default_done, key=key_done)
            item["done_sets"] = int(done)

    if delete_indices:
        for i in sorted(delete_indices, reverse=True):
            del st.session_state.plan[i]
        st.success(f"{len(delete_indices)}개 항목을 삭제했습니다."); st.rerun()

    c_a, c_b, _ = st.columns([1,1,2])
    with c_a:
        if st.button("🗑️ 전체 비우기"):
            st.session_state.plan = []; st.success("모든 계획을 삭제했습니다."); st.rerun()
    with c_b:
        if st.button("💾 오늘 완료 기록 저장"):
            today = date.today().strftime("%Y-%m-%d")
            saved = 0
            for item in st.session_state.plan:
                volume = int(item["weight"]) * int(item["reps"]) * int(item.get("done_sets",0))
                append_log_row([
                    today, st.session_state.nickname, st.session_state.goal, split,
                    item["part"], item["name"], int(item["sets"]), int(item["reps"]),
                    int(item["weight"]), int(item.get("done_sets",0)), volume
                ])
                saved += 1
            st.success(f"{saved}개 기록을 저장했습니다.")