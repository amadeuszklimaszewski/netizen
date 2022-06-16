from abc import ABCMeta, abstractmethod
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Template
from pydantic import BaseModel
from src.apps.emails.schemas import EmailSchema
from src.settings import EmailSettings, settings


class EmailBackendABC(metaclass=ABCMeta):
    def __init__(self):
        self.config = ConnectionConfig(**EmailSettings().dict())

    @abstractmethod
    async def send_email(
        self,
    ) -> None:
        pass


class ConsoleEmailBackend(EmailBackendABC):
    def _get_html_template(self, template_name) -> Template:
        with open(settings.TEMPLATE_FOLDER / template_name, "r") as template_file:
            template = Template(template_file.read())
        return template

    async def send_email(self, schema: EmailSchema, body_schema: BaseModel) -> None:
        template: Template = self._get_html_template(schema.template_name)
        print(template.render(**body_schema.dict()))


class FastAPIMailBackend(EmailBackendABC):
    async def send_email(self, schema: EmailSchema, body_schema: BaseModel) -> None:
        message = MessageSchema(
            subject=schema.subject,
            recipients=schema.recipients,
            template_body=body_schema.dict(),
        )

        fast_mail = FastMail(self.config)
        await fast_mail.send_message(message, template_name=schema.template_name)


class EmailService:
    ...
