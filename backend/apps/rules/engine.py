"""Motor de reglas dinámico (Python puro, sin Django).

Cada tipo de espacio de trabajo tiene su propia función de reglas. El motor recibe
los gastos como `ExpenseData` y devuelve una lista de `Alert`.
Las recomendaciones son solo informativas: no hay conexión con portales gubernamentales.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, List, Optional, Sequence

from .catalog import is_deductible

MONTHLY = "mensual"
YEARLY = "anual"
CENT = Decimal("0.01")
ZERO = Decimal("0.00")


@dataclass(frozen=True)
class ExpenseData:
    id: Optional[int]
    name: str
    amount: Decimal
    category: str
    frequency: str = MONTHLY
    cut_date: Optional[date] = None


@dataclass(frozen=True)
class Alert:
    level: str  # "warning" | "info"
    code: str
    message: str
    expense_id: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


def monthly_amount(expense: ExpenseData) -> Decimal:
    """Monto normalizado a mensual (los pagos anuales se dividen entre 12)."""
    if expense.frequency == YEARLY:
        return (expense.amount / 12).quantize(CENT, rounding=ROUND_HALF_UP)
    return expense.amount.quantize(CENT, rounding=ROUND_HALF_UP)


def monthly_total(expenses: Iterable[ExpenseData]) -> Decimal:
    return sum((monthly_amount(e) for e in expenses), ZERO)


def deductible_monthly(expenses: Iterable[ExpenseData]) -> Decimal:
    return sum((monthly_amount(e) for e in expenses if is_deductible(e.category)), ZERO)


def _universitario(expenses: Sequence[ExpenseData], budget: Optional[Decimal]) -> List[Alert]:
    if budget is None:
        return []
    total = monthly_total(expenses)
    if total > budget:
        return [Alert(
            "warning",
            "PRESUPUESTO_EXCEDIDO",
            f"Presupuesto académico excedido: gastas ${total:,.2f} al mes y tu límite es ${budget:,.2f}.",
        )]
    return []


def _negocio(expenses: Sequence[ExpenseData]) -> List[Alert]:
    alerts: List[Alert] = []
    for e in expenses:
        if is_deductible(e.category):
            alerts.append(Alert(
                "info",
                "SOLICITAR_FACTURA",
                f"Solicite factura (CFDI) por «{e.name}»: la categoría «{e.category}» es deducible.",
                e.id,
            ))
        else:
            alerts.append(Alert(
                "warning",
                "NO_DEDUCIBLE",
                f"Gasto no deducible: «{e.name}» (categoría «{e.category}»).",
                e.id,
            ))
    return alerts


def evaluate(kind: str, expenses: Sequence[ExpenseData], monthly_budget: Optional[Decimal] = None) -> List[Alert]:
    """Evalúa las reglas del espacio de trabajo `kind`."""
    if kind == "universitario":
        return _universitario(expenses, monthly_budget)
    if kind == "negocio":
        return _negocio(expenses)
    return []  # personal: sin reglas


def alerts_for_expense(alerts: Iterable[Alert], expense_id: Optional[int]) -> List[Alert]:
    """Alertas de un gasto concreto + las del espacio completo (expense_id=None)."""
    return [a for a in alerts if a.expense_id is None or a.expense_id == expense_id]
