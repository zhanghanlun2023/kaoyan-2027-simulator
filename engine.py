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


def score_paper(paper: list[dict], answers: dict[str, object]) -> dict:
    earned = 0
    possible = sum(q["points"] for q in paper)
    chapter_stats: dict[str, dict[str, int]] = {}
    details = []
    for q in paper:
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
        "accuracy": (sum(d["correct"] for d in details) / len(details)) if details else 0,
        "chapter_stats": chapter_stats,
        "details": details,
    }

