"""
conftest.py — Configuración global de pytest para la suite E2E de Cal.com.
Proporciona los fixtures de WebDriver compartidos por todas las pruebas.

Proyecto integrador: Cal.com (https://github.com/UP240080/EyMDSW-Calcom)
Asignatura: Estándares y Métricas para el Desarrollo de Software
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# ---------------------------------------------------------------------------
# Constantes de entorno
# ---------------------------------------------------------------------------
BASE_URL = "http://localhost:3000"          # URL base de la instancia Cal.com
IMPLICIT_WAIT = 0                          # Se usan esperas explícitas; NO implícitas
PAGE_LOAD_TIMEOUT = 30                     # segundos máximos para cargar una página
EXPLICIT_WAIT_TIMEOUT = 15                 # segundos por defecto en WebDriverWait


def pytest_addoption(parser):
    """Permite pasar --headless desde la línea de comandos para CI."""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Ejecutar el navegador en modo headless (sin interfaz gráfica).",
    )


@pytest.fixture(scope="session")
def headless(request):
    return request.config.getoption("--headless")


@pytest.fixture(scope="function")
def driver(headless):
    """
    Fixture principal: crea y cierra un WebDriver de Chrome por cada prueba.

    Scope 'function' garantiza aislamiento total entre pruebas:
    ninguna prueba hereda el estado (cookies, sesión) de la anterior.
    """
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless=new")   # API headless moderna (Chrome ≥112)

    # Opciones recomendadas para entornos CI/CD y estabilidad general
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")

    # Service sin ruta explícita: usa el chromedriver que encuentre en el PATH
    service = Service()
    browser = webdriver.Chrome(service=service, options=chrome_options)

    browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    # NO se usa implicit_wait; todas las esperas son explícitas (WebDriverWait)

    yield browser   # entrega el driver a la prueba

    browser.quit()  # teardown garantizado incluso si la prueba falla


@pytest.fixture(scope="function")
def base_url():
    """Fixture de configuración que expone la URL base."""
    return BASE_URL
