from pydantic import BaseModel


class EmailSchema(BaseModel):
    subject: str
    recipients: tuple[str]
    template_name: str


class AccountConfirmationEmailBodySchema(BaseModel):
    token: str
