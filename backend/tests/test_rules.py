import unittest
from decimal import Decimal

from apps.rules.engine import (
    ExpenseData, alerts_for_expense, deductible_monthly, evaluate, monthly_amount, monthly_total,
)


def exp(id, name, amount, category, frequency="mensual"):
    return ExpenseData(id=id, name=name, amount=Decimal(str(amount)), category=category, frequency=frequency)


class MontosTests(unittest.TestCase):
    def test_pago_anual_se_normaliza_a_mensual(self):
        self.assertEqual(monthly_amount(exp(1, "Dominio", 1200, "Software", "anual")), Decimal("100.00"))

    def test_total_mensual_mezcla_periodicidades(self):
        gastos = [exp(1, "A", 200, "Software"), exp(2, "B", 1200, "Software", "anual")]
        self.assertEqual(monthly_total(gastos), Decimal("300.00"))


class UniversitarioTests(unittest.TestCase):
    def test_alerta_si_supera_presupuesto(self):
        gastos = [exp(1, "IDE", 900, "Software"), exp(2, "Curso", 700, "Cursos")]
        alertas = evaluate("universitario", gastos, Decimal("1500"))
        self.assertEqual([a.code for a in alertas], ["PRESUPUESTO_EXCEDIDO"])
        self.assertIn("Presupuesto académico excedido", alertas[0].message)

    def test_sin_alerta_si_esta_dentro_del_presupuesto(self):
        self.assertEqual(evaluate("universitario", [exp(1, "IDE", 900, "Software")], Decimal("1500")), [])

    def test_sin_presupuesto_no_hay_alerta(self):
        self.assertEqual(evaluate("universitario", [exp(1, "IDE", 9000, "Software")], None), [])

    def test_igual_al_presupuesto_no_es_exceso(self):
        self.assertEqual(evaluate("universitario", [exp(1, "IDE", 1500, "Software")], Decimal("1500")), [])


class NegocioTests(unittest.TestCase):
    def test_categoria_deducible_pide_factura(self):
        alertas = evaluate("negocio", [exp(7, "Hosting", 150, "Software")])
        self.assertEqual(alertas[0].code, "SOLICITAR_FACTURA")
        self.assertEqual(alertas[0].expense_id, 7)
        self.assertTrue(alertas[0].message.startswith("Solicite factura"))

    def test_categoria_no_deducible(self):
        alertas = evaluate("negocio", [exp(8, "Cena", 850, "Entretenimiento")])
        self.assertEqual(alertas[0].code, "NO_DEDUCIBLE")
        self.assertIn("Gasto no deducible", alertas[0].message)

    def test_categoria_ignora_mayusculas_y_espacios(self):
        alertas = evaluate("negocio", [exp(1, "Hosting", 150, "  SOFTWARE ")])
        self.assertEqual(alertas[0].code, "SOLICITAR_FACTURA")

    def test_total_deducible_mensual(self):
        gastos = [exp(1, "Hosting", 150, "Software"), exp(2, "Cena", 850, "Entretenimiento")]
        self.assertEqual(deductible_monthly(gastos), Decimal("150.00"))


class PersonalTests(unittest.TestCase):
    def test_personal_no_tiene_reglas(self):
        self.assertEqual(evaluate("personal", [exp(1, "Netflix", 219, "Streaming")], Decimal("1")), [])


class FiltroTests(unittest.TestCase):
    def test_alertas_de_un_gasto_incluyen_las_del_espacio(self):
        gastos = [exp(1, "A", 900, "Software"), exp(2, "B", 900, "Cursos")]
        alertas = evaluate("universitario", gastos, Decimal("1000"))
        self.assertEqual(len(alerts_for_expense(alertas, 1)), 1)  # la del espacio (expense_id None)

        negocio = evaluate("negocio", [exp(1, "A", 1, "Software"), exp(2, "B", 1, "Otros")])
        self.assertEqual([a.expense_id for a in alerts_for_expense(negocio, 2)], [2])


if __name__ == "__main__":
    unittest.main()
