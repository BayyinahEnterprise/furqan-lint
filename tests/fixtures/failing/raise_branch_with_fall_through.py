"""D24 must still fire: one branch raises, but another falls through.

v1.0.1 true-positive guard for the raise-terminal fix. Treating
``raise`` as terminal must not hide a genuinely missing return:
when ``n == 0`` neither branch runs and the function returns None
despite declaring ``-> str``.
"""

from __future__ import annotations


def classify(n: int) -> str:
    if n > 0:
        return "positive"
    elif n < 0:
        raise ValueError("negative")
