# app/constants.py — 상수/프리셋

FILE_PATH = "workout_app.xlsx"
S_EX, S_LOG, S_PROF, S_MEAL = "exercises", "logs", "profiles", "meals"

GOALS   = ["다이어트", "벌크업", "체력 증진", "근력 강화"]
SPLITS  = ["전신", "상하체 2분할", "3분할(가슴/등/하체)"]
GENDERS = ["남성", "여성"]
MEAL_TYPES = ["아침", "점심", "저녁"]

DEFAULT_DB = {
    "가슴": ["벤치프레스", "푸쉬업", "덤벨 플라이"],
    "등": ["랫풀다운", "바벨 로우", "풀업"],
    "하체": ["스쿼트", "레그프레스", "런지"],
    "어깨": ["숄더프레스", "사이드 레터럴레이즈", "리어델트"],
    "팔": ["바벨 컬", "케이블 푸쉬다운", "해머 컬"],
    "전신": ["버피", "케틀벨 스윙", "데드리프트"]
}

GOAL_PRESET = {
    "다이어트": {"sets": 3, "reps": 12, "intensity": "중간"},
    "벌크업": {"sets": 4, "reps": 8,  "intensity": "높음"},
    "체력 증진": {"sets": 3, "reps": 15, "intensity": "중간"},
    "근력 강화": {"sets": 5, "reps": 5,  "intensity": "높음"},
}

MEAL_HEADERS = ["date", "nick", "meal_type", "menu", "main", "grams", "count", "times"]