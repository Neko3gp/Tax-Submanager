"""Cálculos del dashboard (Python puro, sin Django)."""
from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Sequence, Tuple

from apps.rules.engine import CENT, YEARLY, ZERO, ExpenseData, monthly_amount


def _clamp_day(year: int, month: int, day: int) -> date:
    return date(year, month, min(day, calendar.monthrange(year, month)[1]))


def add_months(year: int, month: int, n: int) -> Tuple[int, int]:
    idx = year * 12 + (month - 1) + n
    return idx // 12, idx % 12 + 1


def next_cut_date(cut_date: date, frequency: str, today: date) -> date:
    """Próxima fecha de corte >= hoy (o la primera, si el pago aún no empieza)."""
    if frequency == YEARLY:
        cand = _clamp_day(today.year, cut_date.month, cut_date.day)
        if cand < today:
            cand = _clamp_day(today.year + 1, cut_date.month, cut_date.day)
    else:
        cand = _clamp_day(today.year, today.month, cut_date.day)
        if cand < today:
            y, m = add_months(today.year, today.month, 1)
            cand = _clamp_day(y, m, cut_date.day)
    return max(cand, cut_date)


def by_category(expenses: Sequence[ExpenseData]) -> List[Tuple[str, Decimal]]:
    totals: Dict[str, Decimal] = defaultdict(lambda: ZERO)
    for e in expenses:
        totals[e.category] += monthly_amount(e)
    return sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))


def upcoming(expenses: Sequence[ExpenseData], today: date, days: int = 30) -> List[Tuple[ExpenseData, date, int]]:
    """Cortes dentro de los próximos `days` días: (gasto, fecha, días restantes)."""
    limit = today + timedelta(days=days)
    result = []
    for e in expenses:
        if e.cut_date is None:
            continue
        nxt = next_cut_date(e.cut_date, e.frequency, today)
        if nxt <= limit:
            result.append((e, nxt, (nxt - today).days))
    return sorted(result, key=lambda r: (r[1], r[0].name))


def projection(expenses: Sequence[ExpenseData], today: date, months: int = 12) -> List[Tuple[str, Decimal]]:
    """Flujo de caja proyectado por mes (los pagos anuales caen completos en su mes)."""
    result = []
    for i in range(months):
        y, m = add_months(today.year, today.month, i)
        total = ZERO
        for e in expenses:
            c = e.cut_date
            if c is not None and (y, m) < (c.year, c.month):
                continue  # el pago aún no empieza
            if e.frequency == YEARLY and (c is None or m != c.month):
                continue
            total += e.amount
        result.append((f"{y:04d}-{m:02d}", total.quantize(CENT)))
    return result
