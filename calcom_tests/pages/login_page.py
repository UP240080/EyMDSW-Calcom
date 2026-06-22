"""
pages/login_page.py — Page Object del módulo de autenticación de Cal.com.

Encapsula todos los localizadores y métodos de negocio relacionados con
la pantalla de inicio de sesión (/auth/login).

Referencia de patrón:
    García, B. (2022). Hands-On Selenium WebDriver with Java. O'Reilly.
    (Capítulos de Page Object Model, adaptados a Python/pytest.)
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Reutiliza la constante de timeout definida en conftest sin importarlo
# (conftest.py inyecta los fixtures; las constantes se duplican aquí para
# mantener las pages desacopladas del módulo de configuración).
DEFAULT_TIMEOUT = 15


class LoginPage:
    """
    Page Object para /auth/login de Cal.com.

    Responsabilidades:
        - Navegar a la página de login.
        - Exponer métodos de negocio (ingresar_credenciales, hacer_login,
          obtener_mensaje_error) en lugar de localizadores crudos.
        - Aplicar WebDriverWait en cada interacción para evitar condiciones
          de carrera sin recurrir a time.sleep.

    Uso típico en una prueba:
        login_page = LoginPage(driver)
        login_page.abrir()
        login_page.hacer_login("usuario@example.com", "contraseña")
        assert login_page.login_exitoso()
    """

    # ------------------------------------------------------------------
    # Localizadores (By, valor) — centralizados para fácil mantenimiento
    # ------------------------------------------------------------------
    _CAMPO_EMAIL     = (By.ID, "email")
    _CAMPO_PASSWORD  = (By.ID, "password")
    _BOTON_INGRESAR  = (By.CSS_SELECTOR, "button[type='submit']")
    _ENLACE_REGISTRO = (By.LINK_TEXT, "Create an account")
    _ENLACE_RECOVERY = (By.LINK_TEXT, "Forgot password?")
    _MENSAJE_ERROR   = (By.CSS_SELECTOR, "[data-testid='login-error'], .text-red-700, .text-error")
    _HEADER_DASHBOARD = (By.CSS_SELECTOR, "[data-testid='dashboard'], h3.text-emphasis, nav[aria-label]")

    LOGIN_URL = "/auth/login"

    def __init__(self, driver, base_url: str = "https://app.cal.com", timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._wait = WebDriverWait(driver, timeout)

    # ------------------------------------------------------------------
    # Métodos de navegación
    # ------------------------------------------------------------------

    def abrir(self) -> "LoginPage":
        """Navega directamente a la página de login y espera que cargue."""
        self.driver.get(f"{self.base_url}{self.LOGIN_URL}")
        self._esperar_elemento_visible(self._CAMPO_EMAIL)
        return self

    # ------------------------------------------------------------------
    # Métodos de interacción (negocio)
    # ------------------------------------------------------------------

    def ingresar_email(self, email: str) -> "LoginPage":
        """Limpia el campo de email y escribe el valor proporcionado."""
        campo = self._esperar_elemento_clickable(self._CAMPO_EMAIL)
        campo.clear()
        campo.send_keys(email)
        return self

    def ingresar_password(self, password: str) -> "LoginPage":
        """Limpia el campo de contraseña y escribe el valor proporcionado."""
        campo = self._esperar_elemento_clickable(self._CAMPO_PASSWORD)
        campo.clear()
        campo.send_keys(password)
        return self

    def click_ingresar(self) -> "LoginPage":
        """Hace clic en el botón de envío del formulario."""
        boton = self._esperar_elemento_clickable(self._BOTON_INGRESAR)
        boton.click()
        return self

    def hacer_login(self, email: str, password: str) -> "LoginPage":
        """Método compuesto: llena el formulario y envía en un solo paso."""
        self.ingresar_email(email)
        self.ingresar_password(password)
        self.click_ingresar()
        return self

    # ------------------------------------------------------------------
    # Métodos de verificación (estado de la página)
    # ------------------------------------------------------------------

    def login_exitoso(self) -> bool:
        """
        Retorna True si el login redirigió al dashboard.
        Usa una espera explícita para dar tiempo a la redirección.
        """
        try:
            self._esperar_elemento_visible(self._HEADER_DASHBOARD)
            return True
        except TimeoutException:
            return False

    def login_fallido(self) -> bool:
        """Retorna True si aparece un mensaje de error tras intentar ingresar."""
        try:
            self._esperar_elemento_visible(self._MENSAJE_ERROR)
            return True
        except TimeoutException:
            return False

    def obtener_mensaje_error(self) -> str:
        """
        Retorna el texto del mensaje de error visible.
        Lanza TimeoutException si no aparece dentro del tiempo de espera.
        """
        elemento = self._esperar_elemento_visible(self._MENSAJE_ERROR)
        return elemento.text.strip()

    def campo_email_vacio(self) -> bool:
        """Verifica si el campo de email no contiene texto (caso de borde)."""
        try:
            campo = self.driver.find_element(*self._CAMPO_EMAIL)
            return campo.get_attribute("value") == ""
        except NoSuchElementException:
            return False

    def pagina_cargada(self) -> bool:
        """Verifica que el campo de email sea visible (página completamente cargada)."""
        try:
            self._esperar_elemento_visible(self._CAMPO_EMAIL)
            return True
        except TimeoutException:
            return False

    def url_actual(self) -> str:
        return self.driver.current_url

    # ------------------------------------------------------------------
    # Métodos auxiliares privados (abstracción de WebDriverWait)
    # ------------------------------------------------------------------

    def _esperar_elemento_visible(self, localizador: tuple):
        """Espera hasta que el elemento sea visible en el DOM."""
        return self._wait.until(
            EC.visibility_of_element_located(localizador),
            message=f"Elemento no visible: {localizador}",
        )

    def _esperar_elemento_clickable(self, localizador: tuple):
        """Espera hasta que el elemento sea clickable."""
        return self._wait.until(
            EC.element_to_be_clickable(localizador),
            message=f"Elemento no clickable: {localizador}",
        )
