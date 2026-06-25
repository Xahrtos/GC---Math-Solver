from __future__ import annotations
import logging
from typing import Literal
from cat import tool

from .core import solve_problem, generate_exercise, check_answer, derivative

log = logging.getLogger(__name__)

Topic = Literal["equations", "factorization", "derivatives", "integrals"]


@tool(examples=[
    "Risolvi l'equazione x**2 - 9 = 0",
    "Risolvi questo problema matematico: 2*x + 5 = 11",
    "Semplifica l'espressione x**2 + 2*x + 1",
    "Svolgi questo calcolo"
])
from cat import tool
from cat.utils import log  # Assicurati che log sia importato correttamente

@tool(examples=[
    "Risolvi l'equazione x**2 - 9 = 0",
    "Risolvi questo problema matematico: 2*x + 5 = 11",
    "Semplifica l'espressione x**2 + 2*x + 1",
    "Svolgi questo calcolo"
])
def math_solve(problem: str, cat):
    """Risolve un problema matematico o un'equazione e fornisce la spiegazione passo passo."""
    log.info(f"[MATH_PLUGIN] math_solve called problem={problem!r}")
    
    # Presumo che solve_problem sia importata o definita altrove nel tuo plugin
    res = solve_problem(problem)
    
    if not res.get("ok"):
        return f"Spiacente, si è verificato un errore nel calcolo: {res.get('error', 'Errore sconosciuto')}"
    
    # Costruiamo l'output in Markdown
    output = []
    output.append(f"# Risoluzione del Problema: {problem}\n")
    
    explanation = res.get("explanation", {})
    steps = explanation.get("steps", [])
    
    if steps:
        output.append("## Passaggi logici:\n")
        for i, step in enumerate(steps, 1):
            output.append(f"### {i}. {step['title']}")
            # Corretto l'invio a capo che rompeva la stringa
            output.append(f"```text\n{step['math']}\n```")
            
            if step.get("note"):
                output.append(f"*{step['note']}*\n")
    
    output.append(f"**Risultato Finale:** {explanation.get('final_answer')}")
    
    return "\n".join(output)


@tool(examples=[
    "Generami un esercizio sulle equazioni",
    "Crea un esercizio di matematica",
    "Fammi fare un esercizio sulle derivate di livello 2"
])
def math_generate_exercise(topic: Topic = "equations", level: int = 1, cat=None):
    """Genera un esercizio di matematica di varie tipologie e livelli con la relativa soluzione."""
    log.info(f"[MATH_PLUGIN] math_generate_exercise called topic={topic!r} level={level!r}")
    
    res = generate_exercise(topic=topic, level=level)
    
    output = []
    output.append("# Nuovo Esercizio di Matematica\n")
    output.append(f"- **Argomento**: {res.get('topic')}")
    output.append(f"- **Risultato atteso (nascosto)**: {res.get('explanation', {}).get('final_answer')}\n")
    output.append(f"**Testo dell'esercizio:**\n{res.get('result', {}).get('statement')}")
    
    return "\n".join(output)


@tool(examples=[
    "Verifica se la mia risposta x=3 è giusta per il problema x**2-9=0",
    "Controlla la mia risposta: x=5",
    "Ho fatto questo esercizio, il risultato è corretto?"
])
def math_check_answer(problem: str, user_answer: str, cat):
    """Verifica se la risposta fornita dall'utente per un determinato problema matematico è corretta o errata."""
    log.info(f"[MATH_PLUGIN] math_check_answer called problem={problem!r} user_answer={user_answer!r}")
    
    res = check_answer(problem=problem, user_answer=user_answer)
    
    output = []
    output.append("# Esito della Verifica\n")
    is_correct = res.get("result", {}).get("ok_answer", False)
    
    if is_correct:
        output.append("🎉 **Corretto!** Ottimo lavoro, la risposta è esatta.")
    else:
        output.append("❌ **Non corretto.** Riprova o controlla i passaggi.")
        expected = res.get("result", {}).get("expected_solutions", [])
        output.append(f"- **Soluzioni attese**: {', '.join(expected)}")
        
    return "\n".join(output)


@tool(examples=[
    "Calcola la derivata di x**3 + 2*x",
    "Trova la derivata prima della funzione",
    "Deriva rispetto a x la funzione sin(x)"
])
def math_derivative(expr: str, var: str = "x", order: int = 1, cat=None):
    """Calcola la derivata di una funzione matematica rispetto a una variabile specifica."""
    log.info(f"[MATH_PLUGIN] math_derivative called expr={expr!r} var={var!r} order={order!r}")
    
    res = derivative(expr, var, order)
    
    if not res.get("ok"):
        return f"Errore nel calcolo della derivata: {res.get('error')}"
        
    output = []
    output.append(f"# Calcolo della Derivata (Ordine {order})\n")
    output.append(f"La derivata della funzione rispetto a *{var}* è:\n")
    output.append(f"```text\n{res.get('explanation', {}).get('final_answer')}\n```")
    
    return "\n".join(output)
