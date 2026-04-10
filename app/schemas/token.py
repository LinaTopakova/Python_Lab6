from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer"
            }
        }
    )

class TokenData(BaseModel):
    email: str | None = None
    scopes: str = ""

class RefreshTokenRequest(BaseModel):
    refresh_token: str