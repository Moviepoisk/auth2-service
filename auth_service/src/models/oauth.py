from pydantic import BaseModel


class UserProviderData(BaseModel):
    grant_type: str = "authorization_code"
    code: str
    client_id: str
    client_secret: str


class ProviderURLs(BaseModel):
    auth_url: str
    token_url: str
    user_info_url: str
