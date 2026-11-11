"""Puente entre el ORM de Django y el motor de reglas (que es Python puro)."""
from apps.rules.engine import ExpenseData, evaluate


def to_data(expense) -> ExpenseData:
    return ExpenseData(
        id=expense.id,
        name=expense.name,
        amount=expense.amount,
        category=expense.category,
        frequency=expense.frequency,
        cut_date=expense.cut_date,
    )


def workspace_data(workspace):
    return [to_data(e) for e in workspace.expenses.all()]


def workspace_alerts(workspace):
    return evaluate(workspace.kind, workspace_data(workspace), workspace.monthly_budget)
