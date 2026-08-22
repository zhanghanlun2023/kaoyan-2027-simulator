import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")


def test_english_passages_match_syllabus_scale():
    bank = json.loads((ROOT / "data" / "english2_bank.json").read_text(encoding="utf-8"))
    section_for_passage = {
        item["passage_id"]: item["section"]
        for item in bank["questions"]
        if item.get("passage_id")
    }
    limits = {
        "英语知识运用（完形填空）": (340, 390, 10),
        "阅读理解A": (360, 430, 30),
        "阅读理解B（新题型）": (450, 550, 10),
    }
    for section, (low, high, expected_count) in limits.items():
        counts = [
            len(WORD_RE.findall(bank["passages"][passage_id]))
            for passage_id, item_section in section_for_passage.items()
            if item_section == section
        ]
        assert len(counts) == expected_count
        assert all(low <= count <= high for count in counts)


def test_english_question_bank_integrity():
    bank = json.loads((ROOT / "data" / "english2_bank.json").read_text(encoding="utf-8"))
    assert len(bank["questions"]) == 520
    assert len({item["id"] for item in bank["questions"]}) == 520
    for item in bank["questions"]:
        if item.get("passage_id"):
            assert item["passage_id"] in bank["passages"]
        if item["type"] in {"single", "multiple"}:
            assert item["answer"] in item["options"]

