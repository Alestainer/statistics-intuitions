"""Task interface for the LLM intuition evals.

Each article in the series contributes one task: how to build stimuli, what to
ask, and how to score an answer. Everything else (running models, scoring,
reporting) is shared.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Trial:
    trial_id: str
    image_path: str
    answer: str                 # the correct option, e.g. "LEFT"
    options: list[str]          # e.g. ["LEFT", "RIGHT"]
    mirror_of: str | None = None  # trial_id this is a left-right mirror of
    meta: dict[str, Any] = field(default_factory=dict)


class Task:
    slug: str = ""
    question: str = ""          # shown to the model, must not hint at the answer

    def build(self, out_dir: str, n: int, seed: int) -> list[Trial]:
        raise NotImplementedError
