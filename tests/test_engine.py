from engine import build_english2_paper, build_management_paper, build_paper, score_paper
from engine import load_json


QUESTIONS = [
    {"id": "a", "subject": "数学一", "chapter": "高等数学", "type": "single", "answer": "A", "points": 5},
    {"id": "b", "subject": "数学一", "chapter": "线性代数", "type": "multiple", "answer": ["A", "C"], "points": 5},
]


def test_build_paper_is_repeatable():
    assert build_paper(QUESTIONS, "数学一", 2, 7) == build_paper(QUESTIONS, "数学一", 2, 7)


def test_score_single_and_multiple():
    result = score_paper(QUESTIONS, {"a": "A", "b": ["C", "A"]})
    assert result["earned"] == 10
    assert result["accuracy"] == 1


def test_university_catalog_counts():
    catalog = load_json("universities.json")
    units = catalog["universities"]
    assert len(units) == 116
    assert sum(item["is_985"] for item in units) == 39
    assert len({item["name"] for item in units}) == 116


def test_question_bank_has_mba_path_and_no_duplicates():
    core = load_json("questions.json")
    management = load_json("questions_199.json")
    english2 = load_json("english2_bank.json")["questions"]
    questions = core + management + english2
    assert len(core) == 245
    assert len(management) == 171
    assert len(english2) == 520
    assert len(questions) == 936
    assert len({q["id"] for q in questions}) == len(questions)
    assert len({(q["subject"], q.get("paper_id", ""), q.get("set_id", q.get("group_id", "")), q["stem"]) for q in questions}) == len(questions)


def test_english2_full_paper_matches_real_section_totals():
    bank = load_json("english2_bank.json")
    paper = build_english2_paper(bank, 2027)
    assert len(paper) == 48
    assert sum(q["points"] for q in paper) == 100
    assert sum(q["points"] for q in paper if q["type"] != "essay") == 60
    assert sum(q["section"] == "英语知识运用（完形填空）" for q in paper) == 20
    assert sum(q["section"] == "阅读理解A" for q in paper) == 20
    assert sum(q["section"] == "阅读理解B（新题型）" for q in paper) == 5


def test_management_full_paper_matches_real_section_totals():
    questions = load_json("questions_199.json")
    paper = build_management_paper(questions, 2027)
    assert len(paper) == 57
    assert sum(q["points"] for q in paper) == 200
    assert sum(q["chapter"] == "数学基础·问题求解" for q in paper) == 15
    assert sum(q["chapter"] == "数学基础·条件充分性判断" for q in paper) == 10
    assert sum(q["chapter"] == "逻辑推理" for q in paper) == 30
    assert sum(q["type"] == "essay" for q in paper) == 2
    assert len({q["group_id"] for q in paper if q.get("group_id")}) == 4
    assert all(sum(q.get("group_id") == group for q in paper) == 3 for group in {q["group_id"] for q in paper if q.get("group_id")})
    assert [q["paper_order"] for q in paper] == list(range(1, 58))


def test_essay_is_excluded_from_automatic_score():
    paper = [
        QUESTIONS[0],
        {"id": "essay", "subject": "管理类综合能力", "chapter": "写作", "type": "essay", "answer": "自评", "points": 35},
    ]
    result = score_paper(paper, {"a": "A", "essay": "我的作文"})
    assert result["earned"] == 5
    assert result["possible"] == 5
    assert result["accuracy"] == 1
    assert result["details"][1]["correct"] is None

