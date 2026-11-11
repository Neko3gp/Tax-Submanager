"""Pruebas de API (requieren Django): python manage.py test"""
import shutil
import tempfile

from django.test import override_settings
from rest_framework.test import APITestCase

from apps.workspaces.models import Workspace


def registrar(client, username):
    res = client.post("/api/auth/register/", {"username": username, "password": "clave12345"}, format="json")
    assert res.status_code == 201, res.content
    return res.json()["access"]


class BaseApiTest(APITestCase):
    def login_as(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def workspace_id(self, kind):
        return next(w["id"] for w in self.client.get("/api/workspaces/").json() if w["kind"] == kind)

    def crear_gasto(self, ws_id, **extra):
        data = {"name": "Hosting", "amount": "150.00", "cut_date": "2026-11-20",
                "category": "Software", "frequency": "mensual", **extra}
        return self.client.post(f"/api/workspaces/{ws_id}/expenses/", data, format="json")


class AutenticacionTests(BaseApiTest):
    def test_registro_crea_los_tres_espacios(self):
        token = registrar(self.client, "ana")
        self.login_as(token)
        kinds = sorted(w["kind"] for w in self.client.get("/api/workspaces/").json())
        self.assertEqual(kinds, ["negocio", "personal", "universitario"])

    def test_sin_token_no_hay_acceso(self):
        self.assertEqual(self.client.get("/api/workspaces/").status_code, 401)

    def test_logout_invalida_el_refresh(self):
        res = self.client.post("/api/auth/register/", {"username": "ana", "password": "clave12345"}, format="json")
        self.login_as(res.json()["access"])
        refresh = res.json()["refresh"]
        self.assertEqual(self.client.post("/api/auth/logout/", {"refresh": refresh}, format="json").status_code, 205)
        self.assertEqual(self.client.post("/api/auth/refresh/", {"refresh": refresh}, format="json").status_code, 401)


class AislamientoTests(BaseApiTest):
    def test_un_usuario_no_ve_ni_toca_el_espacio_de_otro(self):
        self.login_as(registrar(self.client, "ana"))
        ws_ana = self.workspace_id("negocio")
        gasto_id = self.crear_gasto(ws_ana).json()["id"]

        self.login_as(registrar(self.client, "beto"))
        self.assertEqual(self.client.get(f"/api/workspaces/{ws_ana}/expenses/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/workspaces/{ws_ana}/dashboard/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/workspaces/{ws_ana}/expenses/{gasto_id}/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/workspaces/{ws_ana}/").status_code, 404)

    def test_los_espacios_del_mismo_usuario_estan_aislados_entre_si(self):
        self.login_as(registrar(self.client, "ana"))
        self.crear_gasto(self.workspace_id("negocio"))
        personal = self.workspace_id("personal")
        self.assertEqual(self.client.get(f"/api/workspaces/{personal}/expenses/").json(), [])


class GastosYReglasTests(BaseApiTest):
    def setUp(self):
        self.login_as(registrar(self.client, "ana"))

    def test_negocio_deducible_devuelve_solicite_factura(self):
        res = self.crear_gasto(self.workspace_id("negocio"), category="Software")
        self.assertEqual(res.status_code, 201)
        self.assertEqual([a["code"] for a in res.json()["alerts"]], ["SOLICITAR_FACTURA"])

    def test_negocio_no_deducible(self):
        res = self.crear_gasto(self.workspace_id("negocio"), name="Cena", category="Entretenimiento")
        self.assertEqual([a["code"] for a in res.json()["alerts"]], ["NO_DEDUCIBLE"])

    def test_universitario_excede_presupuesto(self):
        ws = self.workspace_id("universitario")  # presupuesto inicial: 1500
        res = self.crear_gasto(ws, name="Curso", amount="1600.00", category="Cursos")
        self.assertEqual([a["code"] for a in res.json()["alerts"]], ["PRESUPUESTO_EXCEDIDO"])

    def test_personal_sin_alertas(self):
        res = self.crear_gasto(self.workspace_id("personal"), name="Netflix", category="Streaming")
        self.assertEqual(res.json()["alerts"], [])

    def test_validaciones(self):
        ws = self.workspace_id("personal")
        self.assertEqual(self.crear_gasto(ws, amount="0").status_code, 400)
        self.assertEqual(self.crear_gasto(ws, name="   ").status_code, 400)
        self.assertEqual(self.crear_gasto(ws, frequency="semanal").status_code, 400)

    def test_editar_y_borrar(self):
        ws = self.workspace_id("personal")
        gid = self.crear_gasto(ws, name="Netflix", category="Streaming").json()["id"]
        res = self.client.patch(f"/api/workspaces/{ws}/expenses/{gid}/", {"amount": "250.00"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["amount"], "250.00")
        self.assertEqual(self.client.delete(f"/api/workspaces/{ws}/expenses/{gid}/").status_code, 204)

    def test_dashboard_incluye_totales_y_proyeccion(self):
        ws = self.workspace_id("negocio")
        self.crear_gasto(ws, amount="150.00", category="Software")
        data = self.client.get(f"/api/workspaces/{ws}/dashboard/").json()
        self.assertEqual(data["monthly_total"], "150.00")
        self.assertEqual(len(data["projection"]), 12)
        self.assertEqual(data["deductible_monthly"], "150.00")


class BackupTests(BaseApiTest):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        override = override_settings(BACKUP_DIR=self.tmp)
        override.enable()
        self.addCleanup(override.disable)
        self.login_as(registrar(self.client, "ana"))

    def test_respaldar_borrar_y_restaurar(self):
        ws = self.workspace_id("negocio")
        self.crear_gasto(ws, name="Hosting")
        nombre = self.client.post("/api/backups/").json()["name"]
        self.assertEqual([b["name"] for b in self.client.get("/api/backups/").json()], [nombre])

        gid = self.client.get(f"/api/workspaces/{ws}/expenses/").json()[0]["id"]
        self.client.delete(f"/api/workspaces/{ws}/expenses/{gid}/")
        self.assertEqual(self.client.get(f"/api/workspaces/{ws}/expenses/").json(), [])

        res = self.client.post(f"/api/backups/{nombre}/restore/")
        self.assertEqual(res.status_code, 200)
        nombres = [e["name"] for e in self.client.get(f"/api/workspaces/{ws}/expenses/").json()]
        self.assertEqual(nombres, ["Hosting"])

    def test_nombre_de_respaldo_invalido(self):
        self.assertEqual(self.client.post("/api/backups/..%2Fsecreto.json/restore/").status_code, 404)
        self.assertEqual(self.client.post("/api/backups/otro.json/restore/").status_code, 404)

    def test_un_usuario_no_restaura_respaldos_de_otro(self):
        nombre = self.client.post("/api/backups/").json()["name"]
        self.login_as(registrar(self.client, "beto"))
        self.assertEqual(self.client.post(f"/api/backups/{nombre}/restore/").status_code, 404)
