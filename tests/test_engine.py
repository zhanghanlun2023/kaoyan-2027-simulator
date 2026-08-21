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
