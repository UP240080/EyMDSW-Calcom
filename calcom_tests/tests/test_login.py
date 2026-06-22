"""
tests/test_login.py — Suite de pruebas E2E para el módulo de autenticación.

Cubre los casos de prueba solicitados en la sección 4.3:
    ✓ Casos válidos     : login con credenciales correctas.
    ✓ Casos de frontera : credenciales exactamente en el límite de validez
                          (email sin @, password de 1 carácter, campos vacíos).
    ✓ Casos de error    : credenciales incorrectas, email con formato inválido.
    ✓ Prueba data-driven: múltiples combinaciones de email/password inválidos.

Restricciones aplicadas:
    - Prohibido time.sleep; todas las esperas usan WebDriverWait (vía LoginPage).
    - Fixture `driver` proviene de conftest.py (scope='function' → aislamiento total).

Referencia metodológica:
    Jorgensen, P. C. (2022). Software Testing: A Craftsman's Approach (5ª ed.). CRC Press.
    García, B. (2022). Hands-On Selenium WebDriver with Java. O'Reilly.
"""

import pytest
from selenium.common.exceptions import TimeoutException
from pages.login_page import LoginPage


# ---------------------------------------------------------------------------
# Datos de prueba (constantes de módulo — no credenciales reales)
# ---------------------------------------------------------------------------
VALID_EMAIL    = "testuser@calcom-qa.example.com"   # cuenta de prueba del equipo
VALID_PASSWORD = "QaP@ss2024!"
INVALID_EMAIL_FORMAT  = "usuario_sin_arroba.com"
INVALID_EMAIL_RANDOM  = "noexiste_xyz99@calcom-qa.example.com"
SHORT_PASSWORD        = "a"
EMPTY_STRING          = ""

BASE_URL = "https://app.cal.com"


# ===========================================================================
# TC-LOGIN-01 — Caso válido: login con credenciales correctas
# ===========================================================================
def test_login_credenciales_validas(driver):
    """
    DADO un usuario registrado con credenciales válidas
    CUANDO completa el formulario de login y hace clic en 'Ingresar'
    ENTONCES debe ser redirigido al dashboard de Cal.com.

    Tipo: caso válido (happy path).
    """
    login = LoginPage(driver, base_url=BASE_URL)
    login.abrir()

    assert login.pagina_cargada(), "La página de login no cargó correctamente."

    login.hacer_login(VALID_EMAIL, VALID_PASSWORD)

    assert login.login_exitoso(), (
        f"Se esperaba redirección al dashboard pero la URL actual es: {login.url_actual()}"
    )


# ===========================================================================
# TC-LOGIN-02 — Caso de error: credenciales incorrectas
# ===========================================================================
def test_login_credenciales_incorrectas(driver):
    """
    DADO un usuario con una contraseña incorrecta
    CUANDO intenta hacer login
    ENTONCES debe ver un mensaje de error en pantalla y permanecer en /auth/login.

    Tipo: caso de error.
    """
    login = LoginPage(driver, base_url=BASE_URL)
    login.abrir()
    login.hacer_login(VALID_EMAIL, "contraseña_incorrecta_999!")

    assert login.login_fallido(), (
        "Se esperaba un mensaje de error por credenciales incorrectas, pero no apareció."
    )
    assert "login" in login.url_actual(), (
        "El usuario no debería haber salido de la página de login con credenciales incorrectas."
    )


# ===========================================================================
# TC-LOGIN-03 — Caso de frontera: campos vacíos
# ===========================================================================
def test_login_campos_vacios(driver):
    """
    DADO un usuario que no ingresa ningún dato
    CUANDO hace clic en el botón de ingresar sin llenar los campos
    ENTONCES el sistema debe mostrar validación del lado del cliente (HTML5)
    o un mensaje de error visible.

    Tipo: caso de frontera (valores límite: cadena vacía).
    """
    login = LoginPage(driver, base_url=BASE_URL)
    login.abrir()
    login.hacer_login(EMPTY_STRING, EMPTY_STRING)

    # El navegador puede bloquear el submit con validación HTML5 nativa
    # (required attribute) o Cal.com puede mostrar su propio mensaje.
    # En ambos casos el usuario NO debe avanzar al dashboard.
    assert not login.login_exitoso(), (
        "No se debe poder acceder al dashboard con campos vacíos."
    )


# ===========================================================================
# TC-LOGIN-04 — Caso de frontera: email sin formato válido
# ===========================================================================
def test_login_email_sin_formato_valido(driver):
    """
    DADO un usuario que ingresa un email sin el símbolo '@'
    CUANDO intenta hacer login
    ENTONCES el sistema debe rechazar el intento (validación HTML5 o mensaje de error).

    Tipo: caso de frontera (valor justo fuera del dominio válido de email).
    """
    login = LoginPage(driver, base_url=BASE_URL)
    login.abrir()
    login.hacer_login(INVALID_EMAIL_FORMAT, VALID_PASSWORD)

    assert not login.login_exitoso(), (
        "Un email sin '@' no debe permitir el acceso al dashboard."
    )


# ===========================================================================
# TC-LOGIN-05 — Caso de error: usuario inexistente
# ===========================================================================
def test_login_usuario_inexistente(driver):
    """
    DADO una dirección de email que no corresponde a ninguna cuenta registrada
    CUANDO el usuario intenta autenticarse con cualquier contraseña
    ENTONCES debe recibir un mensaje de error (no un 500 ni acceso al dashboard).

    Tipo: caso de error (email formalmente válido pero sin cuenta asociada).
    """
    login = LoginPage(driver, base_url=BASE_URL)
    login.abrir()
    login.hacer_login(INVALID_EMAIL_RANDOM, "cualquierContraseña123!")

    assert login.login_fallido(), (
        "Se esperaba un error por usuario inexistente, pero el sistema no mostró feedback."
    )
    assert not login.login_exitoso(), (
        "Un email sin cuenta asociada no debe permitir acceso al dashboard."
    )


# ===========================================================================
# TC-LOGIN-06 — Prueba DATA-DRIVEN con @pytest.mark.parametrize
# ===========================================================================

# Conjunto de datos: (email, password, descripcion_del_caso)
CREDENCIALES_INVALIDAS = [
    ("",                              "",                      "ambos_campos_vacios"),
    (INVALID_EMAIL_FORMAT,            VALID_PASSWORD,          "email_sin_arroba"),
    (VALID_EMAIL,                     SHORT_PASSWORD,          "password_de_1_caracter"),
    (INVALID_EMAIL_RANDOM,            "P@ss!2024",             "email_inexistente"),
    ("usuario@",                      VALID_PASSWORD,          "email_dominio_faltante"),
    ("@dominio.com",                  VALID_PASSWORD,          "email_sin_usuario"),
    (VALID_EMAIL,                     EMPTY_STRING,            "password_vacio"),
]


@pytest.mark.parametrize(
    "email, password, caso",
    CREDENCIALES_INVALIDAS,
    ids=[c[2] for c in CREDENCIALES_INVALIDAS],  # IDs legibles en el reporte
)
def test_login_credenciales_invalidas_parametrizado(driver, email, password, caso):
    """
    Prueba data-driven: verifica que ninguna combinación de credenciales inválidas
    permite acceder al dashboard de Cal.com.

    Casos cubiertos (7 combinaciones):
        1. Ambos campos vacíos.
        2. Email sin '@'.
        3. Password de 1 carácter (longitud mínima de frontera).
        4. Email con formato válido pero cuenta inexistente.
        5. Email con dominio faltante ("usuario@").
        6. Email sin parte de usuario ("@dominio.com").
        7. Password vacío.

    Tipo: data-driven (Jorgensen, 2022 — partición de equivalencia y valores límite).
    """
    login = LoginPage(driver, base_url=BASE_URL)
    login.abrir()
    login.hacer_login(email, password)

    assert not login.login_exitoso(), (
        f"[{caso}] La combinación email='{email}' / password='{password}' "
        f"NO debería permitir acceso al dashboard."
    )
