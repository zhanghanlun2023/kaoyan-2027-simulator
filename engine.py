from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Iterable

DATA_DIR = Path(__file__).parent / "data"


def load_json(name: str):
    with (DATA_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def stable_seed(*parts: object) -> int:
    raw = "|".join(map(str, parts)).encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:12], 16)


def build_paper(
    questions: list[dict], subject: str, count: int, seed: int, chapters: Iterable[str] | None = None
) -> list[dict]:
    allowed = set(chapters or [])
    pool = [
        q for q in questions
        if q["subject"] == subject and (not allowed or q["chapter"] in allowed)
    ]
    rng = random.Random(seed)
    rng.shuffle(pool)
    return pool[: min(count, len(pool))]


def build_english2_paper(bank: dict, seed: int) -> list[dict]:
    """Build one complete English II paper using the official section blueprint."""
    rng = random.Random(seed)
    by_section: dict[str, dict[str, list[dict]]] = {}
    for question in bank["questions"]:
        by_section.setdefault(question["section"], {}).setdefault(question["set_id"], []).append(question)

    plan = [
        ("英语知识运用（完形填空）", 1),
        ("阅读理解A", 4),
        ("阅读理解B（新题型）", 1),
        ("英译汉", 1),
        ("应用文写作", 1),
        ("图表/情境作文", 1),
    ]
    paper = []
    for section, set_count in plan:
        set_ids = sorted(by_section[section])
        chosen = rng.sample(set_ids, set_count)
        for set_id in chosen:
            paper.extend(sorted(by_section[section][set_id], key=lambda q: q["order"]))
    return paper


def score_paper(paper: list[dict], answers: dict[str, object]) -> dict:
    earned = 0
    possible = sum(q["points"] for q in paper if q["type"] != "essay")
    chapter_stats: dict[str, dict[str, int]] = {}
    details = []
    for q in paper:
        if q["type"] == "essay":
            details.append({"question": q, "actual": answers.get(q["id"]), "correct": None, "earned": 0})
            continue
        expected = q["answer"]
        actual = answers.get(q["id"])
        if q["type"] == "multiple":
            correct = sorted(actual or []) == sorted(expected)
        else:
            correct = actual == expected
        points = q["points"] if correct else 0
        earned += points
        stat = chapter_stats.setdefault(q["chapter"], {"correct": 0, "total": 0})
        stat["total"] += 1
        stat["correct"] += int(correct)
        details.append({"question": q, "actual": actual, "correct": correct, "earned": points})
    return {
        "earned": earned,
        "possible": possible,
        "accuracy": (
            sum(d["correct"] for d in details if d["correct"] is not None)
            / sum(d["correct"] is not None for d in details)
        ) if any(d["correct"] is not None for d in details) else 0,
        "chapter_stats": chapter_stats,
        "details": details,
    }

