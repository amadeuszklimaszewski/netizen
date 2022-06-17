from pydantic import BaseModel


class TokenOutputSchema(BaseModel):
    access_token: str
