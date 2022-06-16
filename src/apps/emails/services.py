from abc import ABCMeta, abstractmethod
from uuid import uuid4
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Template
from pydantic import BaseModel
from fastapi_another_jwt_auth import AuthJWT
from src.apps.emails.schemas import AccountConfirmationEmailBodySchema, EmailSchema
from src.settings import EmailSettings, settings


class EmailBaseBackend(metaclass=ABCMeta):
    def __init__(self):
        self.config = ConnectionConfig(**EmailSettings().dict())

    @classmethod
    @abstractmethod
    async def send_email(
        self,
    ) -> None:
        pass


class ConsoleEmailBackend(EmailBaseBackend):
    @classmethod
    def _get_html_template(cls, template_name) -> Template:
        with open(settings.TEMPLATE_FOLDER / template_name, "r") as template_file:
            template = Template(template_file.read())
        return template

    @classmethod
    async def send_email(cls, schema: EmailSchema, body_schema: BaseModel) -> None:
        template: Template = cls._get_html_template(schema.template_name)
        print(template.render(**body_schema.dict()))


class FastAPIMailBackend(EmailBaseBackend):
    @classmethod
    async def send_email(cls, schema: EmailSchema, body_schema: BaseModel) -> None:
        message = MessageSchema(
            subject=schema.subject,
            recipients=schema.recipients,
            template_body=body_schema.dict(),
        )

        fast_mail = FastMail(cls.config)
        await fast_mail.send_message(message, template_name=schema.template_name)


class EmailService:
    async def send_activation_email(
        self, email: str, token: str, email_backend: EmailBaseBackend
    ) -> None:
        schema = EmailSchema(
            subject="Confirm your Netizen account",
            template_name="email_confirmation.html",
            recipients=(email,),
        )
        body_schema = AccountConfirmationEmailBodySchema(token=token)
        await email_backend.send_email(schema=schema, body_schema=body_schema)
