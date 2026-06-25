from __future__ import annotations

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    convert_xor,
    implicit_multiplication_application,
)
from typing import Dict, Any, Literal, List, Optional
import random
import sympy as sp

Topic = Literal["equations", "factorization", "derivatives", "integrals"]

_TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)

_ALLOWED_LOCAL_DICT = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sqrt": sp.sqrt,
    "log": sp.log,
    "ln": sp.log,
    "exp": sp.exp,
    "pi": sp.pi,
    "E": sp.E,
}


def parse_user_expr(text: str) -> sp.Expr:
    return parse_expr(
        text.strip(),
        transformations=_TRANSFORMATIONS,
        local_dict=_ALLOWED_LOCAL_DICT,
        evaluate=True,
    )


def _mk_response(
    *,
    tool_name: str,
    topic: str,
    input_data: Dict[str, Any],
    result: Dict[str, Any],
    steps: List[Dict[str, str]],
    final_answer: str,
    sympy_pretty: str = "",
    sympy_raw: str = "",
    ok: bool = True,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ok": ok,
        "tool": tool_name,
        "plugin_used": "math_solver",
        "topic": topic,
        "input": input_data,
        "result": result,
        "explanation": {"steps": steps, "final_answer": final_answer},
        "sympy": {"pretty": sympy_pretty, "raw": sympy_raw},
    }
    if error:
        payload["error"] = error
    return payload


def _format_eq(eq: sp.Eq) -> str:
    return sp.pretty(eq, use_unicode=True)


def _solve_linear_equation(eq: sp.Eq, x: sp.Symbol) -> Dict[str, Any]:
    left = sp.expand(eq.lhs)
    right = sp.expand(eq.rhs)

    a = sp.simplify(sp.diff(left, x))
    b = sp.simplify(left.subs(x, 0))

    if sp.simplify(left - (a * x + b)) != 0:
        sol = sp.solve(eq, x)
        steps = [
            {"title": "Imposto l'equazione", "math": _format_eq(eq), "note": ""},
            {"title": "Risolvo con SymPy", "math": ", ".join([sp.sstr(s) for s in sol]), "note": "Forma non lineare semplice."},
        ]
        final_answer = "; ".join([f"x = {sp.sstr(s)}" for s in sol]) if sol else "Nessuna soluzione trovata."
        return {"solutions": sol, "steps": steps, "final_answer": final_answer}

    steps: List[Dict[str, str]] = []
    steps.append({"title": "Imposto l'equazione", "math": _format_eq(sp.Eq(a * x + b, right)), "note": ""})
    steps.append(
        {
            "title": "Isolo il termine con x",
            "math": _format_eq(sp.Eq(a * x, right - b)),
            "note": f"Sottraggo {sp.sstr(b)} a entrambi i membri.",
        }
    )

    if a == 0:
        k = sp.simplify(right - b)
        if sp.simplify(k) == 0:
            final_answer = "Infinitamente molte soluzioni (identità)."
            solutions = []
        else:
            final_answer = "Nessuna soluzione (contraddizione)."
            solutions = []
        steps.append({"title": "Caso particolare", "math": _format_eq(sp.Eq(0, k)), "note": "Il coefficiente di x è 0."})
        return {"solutions": solutions, "steps": steps, "final_answer": final_answer}

    x_expr = sp.simplify((right - b) / a)
    steps.append(
        {
            "title": "Divido per il coefficiente di x",
            "math": _format_eq(sp.Eq(x, x_expr)),
            "note": f"Divido entrambi i membri per {sp.sstr(a)}.",
        }
    )

    return {"solutions": [x_expr], "steps": steps, "final_answer": f"x = {sp.sstr(x_expr)}"}


def solve_problem(problem: str) -> Dict[str, Any]:
    x = sp.Symbol("x")
    try:
        if "=" in problem:
            left, right = problem.split("=", 1)
            eq = sp.Eq(parse_user_expr(left), parse_user_expr(right))
            solved = _solve_linear_equation(eq, x)
            return _mk_response(
                tool_name="math_solve",
                topic="equations",
                input_data={"problem": problem},
                result={"solutions": [sp.sstr(s) for s in solved["solutions"]]},
                steps=solved["steps"],
                final_answer=solved["final_answer"],
                sympy_pretty=_format_eq(eq),
                sympy_raw=sp.sstr(eq),
            )

        expr = parse_user_expr(problem)
        simp = sp.simplify(expr)
        steps = [
            {"title": "Interpreto l'espressione", "math": sp.pretty(expr, use_unicode=True), "note": ""},
            {"title": "Semplifico", "math": sp.pretty(simp, use_unicode=True), "note": "Semplificazione algebrica con SymPy."},
        ]
        return _mk_response(
            tool_name="math_solve",
            topic="expression",
            input_data={"problem": problem},
            result={"simplified": sp.sstr(simp)},
            steps=steps,
            final_answer=sp.sstr(simp),
            sympy_pretty=sp.pretty(simp, use_unicode=True),
            sympy_raw=sp.sstr(simp),
        )
    except Exception as e:
        return _mk_response(
            tool_name="math_solve",
            topic="unknown",
            input_data={"problem": problem},
            result={},
            steps=[],
            final_answer="",
            ok=False,
            error=str(e),
        )


def generate_exercise(topic: Topic = "equations", level: int = 1) -> Dict[str, Any]:
    x = sp.Symbol("x")

    if topic == "equations":
        if level <= 1:
            a = random.choice([1, 2, 3, -1, -2, -3])
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            eq = sp.Eq(a * x + b, c)
        else:
            a1 = random.choice([1, 2, 3, -1, -2])
            b1 = random.randint(-10, 10)
            a2 = random.choice([0, 1, -1, 2])
            b2 = random.randint(-10, 10)
            eq = sp.Eq(a1 * x + b1, a2 * x + b2)

        solved = _solve_linear_equation(eq, x)
        return _mk_response(
            tool_name="math_generate_exercise",
            topic="equations",
            input_data={"topic": topic, "level": level},
            result={
                "statement": f"Risolvi l'equazione: {sp.sstr(eq.lhs)} = {sp.sstr(eq.rhs)}",
                "solutions": [sp.sstr(s) for s in solved["solutions"]],
            },
            steps=solved["steps"],
            final_answer=solved["final_answer"],
            sympy_pretty=_format_eq(eq),
            sympy_raw=sp.sstr(eq),
        )

    if topic == "derivatives":
        if level <= 1:
            a = random.choice([1, 2, 3, -1, -2])
            b = random.randint(-5, 5)
            c = random.randint(-10, 10)
            n = random.choice([2, 3, 4])
            f = a * x**n + b * x + c
        else:
            p = x + random.randint(-5, 5)
            q = random.choice([x**2 + 1, 2 * x + 3, x - 1])
            f = sp.expand(p * q)

        d = sp.diff(f, x)
        steps = [
            {"title": "Funzione", "math": sp.pretty(f, use_unicode=True), "note": ""},
            {"title": "Derivata", "math": sp.pretty(d, use_unicode=True), "note": "Calcolo con SymPy."},
        ]
        return _mk_response(
            tool_name="math_generate_exercise",
            topic="derivatives",
            input_data={"topic": topic, "level": level},
            result={"statement": f"Calcola la derivata di f(x) = {sp.sstr(f)}", "derivative": sp.sstr(d)},
            steps=steps,
            final_answer=f"f'(x) = {sp.sstr(d)}",
            sympy_pretty=sp.pretty(d, use_unicode=True),
            sympy_raw=sp.sstr(d),
        )

    return generate_exercise(topic="equations", level=level)


def check_answer(problem: str, user_answer: str) -> Dict[str, Any]:
    x = sp.Symbol("x")
    try:
        if "=" in problem:
            left, right = problem.split("=", 1)
            eq = sp.Eq(parse_user_expr(left), parse_user_expr(right))
            sol = sp.solve(eq, x)

            ua = user_answer.strip().replace(";", ",")
            parts = [p.strip().replace("x=", "") for p in ua.split(",") if p.strip()]
            if not parts:
                parts = [ua.replace("x=", "").strip()]

            parsed_user = [parse_user_expr(p) for p in parts]
            ok = set(sp.sstr(s) for s in parsed_user) == set(sp.sstr(s) for s in sol)

            return _mk_response(
                tool_name="math_check_answer",
                topic="equations",
                input_data={"problem": problem, "user_answer": user_answer},
                result={"ok_answer": bool(ok), "expected_solutions": [sp.sstr(s) for s in sol]},
                steps=[
                    {"title": "Equazione", "math": _format_eq(eq), "note": ""},
                    {"title": "Soluzioni attese", "math": ", ".join([sp.sstr(s) for s in sol]), "note": ""},
                    {"title": "Risposta utente", "math": ", ".join([sp.sstr(s) for s in parsed_user]), "note": ""},
                ],
                final_answer="Corretto." if ok else "Non corretto.",
                sympy_pretty=_format_eq(eq),
                sympy_raw=sp.sstr(eq),
            )

        expr = parse_user_expr(problem)
        ua = parse_user_expr(user_answer)
        ok = sp.simplify(expr - ua) == 0
        return _mk_response(
            tool_name="math_check_answer",
            topic="expression",
            input_data={"problem": problem, "user_answer": user_answer},
            result={"ok_answer": bool(ok)},
            steps=[
                {"title": "Espressione", "math": sp.pretty(expr, use_unicode=True), "note": ""},
                {"title": "Risposta utente", "math": sp.pretty(ua, use_unicode=True), "note": ""},
                {"title": "Verifica equivalenza", "math": "simplify(expr - answer) == 0", "note": f"Risultato: {bool(ok)}"},
            ],
            final_answer="Corretto." if ok else "Non corretto.",
            sympy_pretty=sp.pretty(expr, use_unicode=True),
            sympy_raw=sp.sstr(expr),
        )
    except Exception as e:
        return _mk_response(
            tool_name="math_check_answer",
            topic="unknown",
            input_data={"problem": problem, "user_answer": user_answer},
            result={},
            steps=[],
            final_answer="",
            ok=False,
            error=str(e),
        )


def derivative(expr: str, var: str = "x", order: int = 1) -> Dict[str, Any]:
    try:
        x = sp.Symbol(var)
        parsed = parse_user_expr(expr)  # FIX
        d = sp.diff(parsed, x, order)

        steps: List[Dict[str, str]] = [
            {"title": "Interpreto la funzione", "math": sp.pretty(parsed, use_unicode=True), "note": f"Variabile: {var}, ordine: {order}"},
            {"title": "Calcolo la derivata", "math": sp.pretty(d, use_unicode=True), "note": "Calcolo con SymPy."},
        ]

        return _mk_response(
            tool_name="math_derivative",
            topic="derivatives",
            input_data={"expr": expr, "var": var, "order": order},
            result={"derivative": sp.sstr(d)},
            steps=steps,
            final_answer=sp.sstr(d),
            sympy_pretty=sp.pretty(d, use_unicode=True),
            sympy_raw=sp.sstr(d),
        )
    except Exception as e:
        return _mk_response(
            tool_name="math_derivative",
            topic="derivatives",
            input_data={"expr": expr, "var": var, "order": order},
            result={},
            steps=[],
            final_answer="",
            ok=False,
            error=str(e),
        )
