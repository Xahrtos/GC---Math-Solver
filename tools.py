from __future__ import annotations

import logging
from typing import Literal
from cat import tool

from .core import solve_problem, generate_exercise, check_answer, derivative

log = logging.getLogger(__name__)

Topic = Literal["equations", "factorization", "derivatives", "integrals"]


@tool
def math_solve(problem: str, cat=None):
    """Risolve un problema matematico e fornisce spiegazione passo passo (JSON)."""
    log.info(f"[MATH_PLUGIN] math_solve called problem={problem!r}")
    return solve_problem(problem)


@tool
def math_generate_exercise(topic: Topic = "equations", level: int = 1, cat=None):
    """Genera un esercizio di matematica con soluzione e passi."""
    log.info(f"[MATH_PLUGIN] math_generate_exercise called topic={topic!r} level={level!r}")
    return generate_exercise(topic=topic, level=level)


@tool
def math_check_answer(problem: str, user_answer: str, cat=None):
    """Verifica la risposta dell'utente a un esercizio/problema."""
    log.info(f"[MATH_PLUGIN] math_check_answer called problem={problem!r} user_answer={user_answer!r}")
    return check_answer(problem=problem, user_answer=user_answer)


@tool
def math_derivative(expr: str, var: str = "x", order: int = 1, cat=None):
    """Calcola la derivata con spiegazione passo-passo (JSON)."""
    log.info(f"[MATH_PLUGIN] math_derivative called expr={expr!r} var={var!r} order={order!r}")
    return derivative(expr=expr, var=var, order=order)