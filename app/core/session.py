# app/core/session.py

class SessionManager:
    """
    Gestor de estado global para la aplicación cliente.
    Almacena el JWT en la memoria RAM durante la ejecución del programa.
    """
    _token = None

    @classmethod
    def set_token(cls, token: str):
        cls._token = token

    @classmethod
    def get_token(cls) -> str:
        return cls._token

    @classmethod
    def clear(cls):
        cls._token = None