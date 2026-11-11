import unittest
from datetime import date
from decimal import Decimal

from apps.dashboard.calculations import add_months, by_category, next_cut_date, projection, upcoming
from apps.rules.engine import ExpenseData


def exp(id, name, amount, category, cut, frequency="mensual"):
    return ExpenseData(id=id, name=name, amount=Decimal(str(amount)), category=category,
                       frequency=frequency, cut_date=cut)


class FechasTests(unittest.TestCase):
    def test_add_months_cruza_de_anio(self):
        self.assertEqual(add_months(2026, 11, 2), (2027, 1))
        self.assertEqual(add_months(2026, 12, 1), (2027, 1))

    def test_corte_mensual_dia_31_se_ajusta_a_fin_de_mes(self):
        self.assertEqual(next_cut_date(date(2026, 1, 31), "mensual", date(2026, 2, 10)), date(2026, 2, 28))

    def test_corte_mensual_ya_paso_este_mes_salta_al_siguiente(self):
        self.assertEqual(next_cut_date(date(2026, 1, 5), "mensual", date(2026, 11, 11)), date(2026, 12, 5))

    def test_corte_mensual_hoy_cuenta_como_proximo(self):
        self.assertEqual(next_cut_date(date(2026, 1, 11), "mensual", date(2026, 11, 11)), date(2026, 11, 11))

    def test_corte_anual(self):
        self.assertEqual(next_cut_date(date(2025, 3, 5), "anual", date(2026, 11, 11)), date(2027, 3, 5))
        self.assertEqual(next_cut_date(date(2025, 12, 1), "anual", date(2026, 11, 11)), date(2026, 12, 1))

    def test_pago_que_aun_no_empieza_usa_su_primera_fecha(self):
        self.assertEqual(next_cut_date(date(2026, 12, 20), "mensual", date(2026, 11, 11)), date(2026, 12, 20))
        self.assertEqual(next_cut_date(date(2027, 3, 5), "anual", date(2026, 2, 1)), date(2027, 3, 5))


class DashboardTests(unittest.TestCase):
    today = date(2026, 11, 11)

    def test_por_categoria_ordena_de_mayor_a_menor(self):
        gastos = [
            exp(1, "A", 100, "Software", date(2026, 11, 15)),
            exp(2, "B", 500, "Renta", date(2026, 11, 20)),
            exp(3, "C", 50, "Software", date(2026, 11, 25)),
        ]
        self.assertEqual(by_category(gastos), [("Renta", Decimal("500.00")), ("Software", Decimal("150.00"))])

    def test_proximos_30_dias(self):
        gastos = [
            exp(1, "Pronto", 10, "X", date(2026, 11, 15)),
            exp(2, "Lejos", 10, "X", date(2026, 12, 20)),     # a 39 días
            exp(3, "Anual lejano", 10, "X", date(2025, 3, 5), "anual"),
        ]
        resultado = upcoming(gastos, self.today)
        self.assertEqual([(e.name, d, left) for e, d, left in resultado], [("Pronto", date(2026, 11, 15), 4)])

    def test_proyeccion_12_meses(self):
        gastos = [
            exp(1, "Mensual", 100, "X", date(2026, 1, 1)),
            exp(2, "Anual", 1200, "X", date(2026, 3, 15), "anual"),
        ]
        meses = projection(gastos, self.today)
        self.assertEqual(len(meses), 12)
        self.assertEqual(meses[0], ("2026-11", Decimal("100.00")))
        self.assertEqual(meses[-1][0], "2027-10")
        marzo = dict(meses)["2027-03"]
        self.assertEqual(marzo, Decimal("1300.00"))  # 100 mensual + 1200 anual
        self.assertEqual(sum(t for _, t in meses), Decimal("2400.00"))

    def test_proyeccion_ignora_meses_previos_al_inicio_del_pago(self):
        meses = dict(projection([exp(1, "Futuro", 100, "X", date(2027, 1, 10))], self.today))
        self.assertEqual(meses["2026-12"], Decimal("0.00"))
        self.assertEqual(meses["2027-01"], Decimal("100.00"))


if __name__ == "__main__":
    unittest.main()
