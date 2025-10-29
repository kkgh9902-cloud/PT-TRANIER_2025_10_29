# app/domain.py — 추천/도메인 로직
from .constants import GOAL_PRESET

def find_part_of_ex(db, ex_name):
    for part, items in db.items():
        if ex_name in items:
            return part
    return "기타"

def recommend_by_split(goal, split, db):
    if split == "전신":
        picks = [("전신",1), ("가슴",1), ("등",1), ("하체",1), ("어깨",1)]
    elif split == "상하체 2분할":
        picks = [("가슴",1), ("등",1), ("어깨",1), ("팔",1), ("하체",1)]
    else:
        picks = [("가슴",2), ("등",2), ("하체",2)]
    base = []
    for part, k in picks:
        if part in db and len(db[part])>0:
            base += db[part][:k]
    preset = GOAL_PRESET.get(goal, {"sets":3,"reps":10,"intensity":"중간"})
    return [{
        "part": find_part_of_ex(db, ex), "name": ex,
        "sets": preset["sets"], "reps": preset["reps"],
        "intensity": preset["intensity"], "weight": 0
    } for ex in base]