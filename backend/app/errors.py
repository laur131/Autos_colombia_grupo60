class DomainError(Exception):
    """Error de negocio: el router lo convierte en respuesta HTTP."""

    def __init__(self, status: int, codigo: str, mensaje: str):
        super().__init__(mensaje)
        self.status, self.codigo, self.mensaje = status, codigo, mensaje
