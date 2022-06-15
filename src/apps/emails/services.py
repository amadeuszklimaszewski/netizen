from abc import ABCMeta, abstractmethod
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Template
from src.settings import EmailSettings


class EmailBackendABC(metaclass=ABCMeta):
    def __init__(self):
        self.config = ConnectionConfig(**EmailSettings().dict())

    @abstractmethod
    async def send_email(
        self,
    ) -> None:
        pass


class ConsoleEmailBackend(EmailBackendABC):
    async def send_email(self) -> None:
        ...


class FastAPIMailBackend(EmailBackendABC):
    async def send_email(self) -> None:
        ...
