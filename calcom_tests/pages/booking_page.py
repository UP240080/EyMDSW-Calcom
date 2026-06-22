"""
pages/booking_page.py — Page Object del flujo de reserva de citas de Cal.com.

Encapsula los localizadores y métodos de negocio de las pantallas de
selección de tipo de evento, calendario de disponibilidad y formulario
de confirmación de reserva.

Este módulo cubre el flujo crítico descrito en la introducción del proyecto:
selección de tipo de evento → elección de fecha/hora → captura de datos →
confirmación.

Referencia de patrón:
    García, B. (2022). Hands-On Selenium WebDriver with Java. O'Reilly.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

DEFAULT_TIMEOUT = 15


class BookingPage:
    """
    Page Object para el flujo de reserva pública de Cal.com.

    La URL pública de reserva sigue el patrón:
        /{username}/{event-slug}

    Este Page Object cubre:
        1. La pantalla de selección de tipo de evento (landing del usuario).
        2. El calendario de disponibilidad.
        3. El formulario de confirmación de datos del invitado.
        4. La pantalla de confirmación de reserva exitosa.

    Uso típico:
        booking = BookingPage(driver, base_url="https://app.cal.com")
        booking.abrir_perfil("demo")
        assert booking.perfil_cargado()
        booking.seleccionar_primer_evento_disponible()
        booking.seleccionar_primera_fecha_disponible()
        booking.seleccionar_primer_horario_disponible()
        booking.completar_formulario("Juan", "juan@mail.com")
        booking.confirmar_reserva()
        assert booking.reserva_confirmada()
    """

    # ------------------------------------------------------------------
    # Localizadores
    # ------------------------------------------------------------------

    # Pantalla de perfil / listado de eventos
    _LISTA_EVENTOS        = (By.CSS_SELECTOR, "[data-testid='event-type-link'], a[href*='/booking']")
    _TITULO_PERFIL        = (By.CSS_SELECTOR, "h1.text-emphasis, h1[data-testid='name']")

    # Calendario
    _DIAS_DISPONIBLES     = (By.CSS_SELECTOR, "button[data-testid='day']:not([disabled])")
    _CALENDARIO           = (By.CSS_SELECTOR, "[data-testid='calendar'], .datepicker")

    # Selector de hora
    _HORAS_DISPONIBLES    = (By.CSS_SELECTOR, "button[data-testid='time']")

    # Formulario de datos del invitado
    _INPUT_NOMBRE         = (By.ID, "name")
    _INPUT_EMAIL          = (By.ID, "email")
    _INPUT_NOTAS          = (By.ID, "notes")
    _BOTON_CONFIRMAR      = (By.CSS_SELECTOR, "button[type='submit'][data-testid='confirm-book-button'], button[type='submit']")

    # Pantalla de confirmación
    _CONFIRMACION_TITULO  = (By.CSS_SELECTOR, "[data-testid='booking-confirmed'], h2.text-emphasis")
    _CONFIRMACION_EMAIL   = (By.CSS_SELECTOR, "[data-testid='attendee-email'], .attendee-email")

    # Mensajes de error en formulario
    _ERROR_EMAIL          = (By.CSS_SELECTOR, "[data-testid='email-error'], p.text-red-700")
    _ERROR_NOMBRE         = (By.CSS_SELECTOR, "[data-testid='name-error']")

    BASE_URL = "https://app.cal.com"

    def __init__(self, driver, base_url: str = BASE_URL, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._wait = WebDriverWait(driver, timeout)

    # ------------------------------------------------------------------
    # Métodos de navegación
    # ------------------------------------------------------------------

    def abrir_perfil(self, username: str) -> "BookingPage":
        """Navega al perfil público de un usuario de Cal.com."""
        self.driver.get(f"{self.base_url}/{username}")
        self._esperar_elemento_visible(self._TITULO_PERFIL)
        return self

    def abrir_evento_directo(self, username: str, event_slug: str) -> "BookingPage":
        """Navega directamente a un tipo de evento específico."""
        self.driver.get(f"{self.base_url}/{username}/{event_slug}")
        self._esperar_elemento_visible(self._CALENDARIO)
        return self

    # ------------------------------------------------------------------
    # Métodos de interacción — selección de evento
    # ------------------------------------------------------------------

    def obtener_eventos_disponibles(self) -> list:
        """Retorna la lista de elementos de tipo de evento visibles en el perfil."""
        try:
            self._esperar_elemento_visible(self._LISTA_EVENTOS)
            return self.driver.find_elements(*self._LISTA_EVENTOS)
        except TimeoutException:
            return []

    def seleccionar_primer_evento_disponible(self) -> "BookingPage":
        """Hace clic en el primer tipo de evento listado en el perfil."""
        eventos = self.obtener_eventos_disponibles()
        if not eventos:
            raise AssertionError("No se encontraron eventos disponibles en el perfil.")
        eventos[0].click()
        self._esperar_elemento_visible(self._CALENDARIO)
        return self

    # ------------------------------------------------------------------
    # Métodos de interacción — calendario
    # ------------------------------------------------------------------

    def obtener_dias_disponibles(self) -> list:
        """Retorna los botones de días habilitados en el calendario."""
        try:
            self._esperar_elemento_visible(self._CALENDARIO)
            return self.driver.find_elements(*self._DIAS_DISPONIBLES)
        except TimeoutException:
            return []

    def seleccionar_primera_fecha_disponible(self) -> "BookingPage":
        """Selecciona el primer día habilitado del calendario."""
        dias = self.obtener_dias_disponibles()
        if not dias:
            raise AssertionError("No se encontraron fechas disponibles en el calendario.")
        dias[0].click()
        self._esperar_elemento_visible(self._HORAS_DISPONIBLES)
        return self

    # ------------------------------------------------------------------
    # Métodos de interacción — selector de horario
    # ------------------------------------------------------------------

    def obtener_horas_disponibles(self) -> list:
        """Retorna los botones de hora disponibles para la fecha seleccionada."""
        try:
            return self.driver.find_elements(*self._HORAS_DISPONIBLES)
        except NoSuchElementException:
            return []

    def seleccionar_primer_horario_disponible(self) -> "BookingPage":
        """Selecciona el primer horario disponible y avanza al formulario."""
        horas = self.obtener_horas_disponibles()
        if not horas:
            raise AssertionError("No se encontraron horarios disponibles para la fecha seleccionada.")
        horas[0].click()
        self._esperar_elemento_visible(self._INPUT_NOMBRE)
        return self

    # ------------------------------------------------------------------
    # Métodos de interacción — formulario de confirmación
    # ------------------------------------------------------------------

    def ingresar_nombre(self, nombre: str) -> "BookingPage":
        campo = self._esperar_elemento_clickable(self._INPUT_NOMBRE)
        campo.clear()
        campo.send_keys(nombre)
        return self

    def ingresar_email(self, email: str) -> "BookingPage":
        campo = self._esperar_elemento_clickable(self._INPUT_EMAIL)
        campo.clear()
        campo.send_keys(email)
        return self

    def ingresar_notas(self, notas: str) -> "BookingPage":
        """Ingresa notas adicionales (campo opcional)."""
        try:
            campo = self._esperar_elemento_clickable(self._INPUT_NOTAS)
            campo.clear()
            campo.send_keys(notas)
        except TimeoutException:
            pass   # El campo de notas es opcional; si no existe, se ignora
        return self

    def completar_formulario(self, nombre: str, email: str, notas: str = "") -> "BookingPage":
        """Método compuesto: llena todos los campos del formulario de reserva."""
        self.ingresar_nombre(nombre)
        self.ingresar_email(email)
        if notas:
            self.ingresar_notas(notas)
        return self

    def confirmar_reserva(self) -> "BookingPage":
        """Hace clic en el botón de confirmación de la reserva."""
        boton = self._esperar_elemento_clickable(self._BOTON_CONFIRMAR)
        boton.click()
        return self

    # ------------------------------------------------------------------
    # Métodos de verificación
    # ------------------------------------------------------------------

    def perfil_cargado(self) -> bool:
        try:
            self._esperar_elemento_visible(self._TITULO_PERFIL)
            return True
        except TimeoutException:
            return False

    def reserva_confirmada(self) -> bool:
        """Retorna True si se muestra la pantalla de confirmación de reserva."""
        try:
            self._esperar_elemento_visible(self._CONFIRMACION_TITULO)
            return True
        except TimeoutException:
            return False

    def hay_error_email(self) -> bool:
        """Retorna True si se muestra un error de validación en el campo email."""
        try:
            self._esperar_elemento_visible(self._ERROR_EMAIL)
            return True
        except TimeoutException:
            return False

    def obtener_texto_error_email(self) -> str:
        elemento = self._esperar_elemento_visible(self._ERROR_EMAIL)
        return elemento.text.strip()

    def url_actual(self) -> str:
        return self.driver.current_url

    def cantidad_eventos(self) -> int:
        return len(self.obtener_eventos_disponibles())

    # ------------------------------------------------------------------
    # Métodos auxiliares privados
    # ------------------------------------------------------------------

    def _esperar_elemento_visible(self, localizador: tuple):
        return self._wait.until(
            EC.visibility_of_element_located(localizador),
            message=f"Elemento no visible: {localizador}",
        )

    def _esperar_elemento_clickable(self, localizador: tuple):
        return self._wait.until(
            EC.element_to_be_clickable(localizador),
            message=f"Elemento no clickable: {localizador}",
        )
