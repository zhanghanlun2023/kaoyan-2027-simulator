from engine import build_paper, score_paper
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
    questions = load_json("questions.json")
    assert len(questions) == 402
    assert sum(q["subject"] == "管理类综合能力" for q in questions) == 125
    assert sum(q["subject"] == "英语二" for q in questions) == 32
    assert len({q["id"] for q in questions}) == len(questions)
    assert len({(q["subject"], q["stem"]) for q in questions}) == len(questions)


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

