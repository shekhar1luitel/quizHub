from pydantic import BaseModel, EmailStr, Field, model_validator

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str

    @model_validator(mode="after")
    def ensure_identifier(self) -> "LoginIn":
        if not self.email and not self.username:
            raise ValueError("Username or email is required")
        if self.username:
            self.username = self.username.strip().lower()
            if not self.username:
                raise ValueError("Username cannot be blank")
        if self.email:
            self.email = self.email.strip().lower()
        return self


class VerifyEmailIn(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    code: str = Field(min_length=6, max_length=6)

    @model_validator(mode="after")
    def ensure_identifiers(self) -> "VerifyEmailIn":
        if not self.email and not self.username:
            raise ValueError("Username or email is required")
        if self.username:
            self.username = self.username.strip().lower()
            if not self.username:
                raise ValueError("Username cannot be blank")
        if self.email:
            self.email = self.email.strip().lower()
        self.code = self.code.strip()
        if not self.code.isdigit():
            raise ValueError("Verification code must be numeric")
        return self


class ResendVerificationIn(BaseModel):
    email: EmailStr | None = None
    username: str | None = None

    @model_validator(mode="after")
    def ensure_identifiers(self) -> "ResendVerificationIn":
        if not self.email and not self.username:
            raise ValueError("Username or email is required")
        if self.username:
            self.username = self.username.strip().lower()
            if not self.username:
                raise ValueError("Username cannot be blank")
        if self.email:
            self.email = self.email.strip().lower()
        return self
