from datetime import datetime
from enum import Enum
import re

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)


class UserRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"


class UserRegisterRequest(BaseModel):
    email: str = Field(
        min_length=3,
        max_length=320
    )
    full_name: str = Field(
        min_length=1,
        max_length=255
    )
    password: str = Field(
        min_length=8,
        max_length=72
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str):
        normalized = value.strip().lower()

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            normalized
        ):

            raise ValueError(
                "A valid email address is required"
            )

        return normalized

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str):
        normalized = value.strip()

        if not normalized:

            raise ValueError(
                "Full name cannot be blank"
            )

        return normalized

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str):

        if len(value.encode("utf-8")) > 72:

            raise ValueError(
                "Password must not exceed 72 UTF-8 bytes"
            )

        return value


class UserLoginRequest(BaseModel):
    email: str = Field(
        min_length=3,
        max_length=320
    )
    password: str = Field(
        min_length=1,
        max_length=72
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str):
        normalized = value.strip().lower()

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            normalized
        ):

            raise ValueError(
                "A valid email address is required"
            )

        return normalized

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str):

        if len(value.encode("utf-8")) > 72:

            raise ValueError(
                "Password must not exceed 72 UTF-8 bytes"
            )

        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ForgotPasswordRequest(BaseModel):

    email: str = Field(
        min_length=3,
        max_length=320
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str):

        return UserRegisterRequest.normalize_email(
            value
        )


class VerifyResetOTPRequest(
    ForgotPasswordRequest
):

    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )


class ResetPasswordRequest(BaseModel):

    reset_token: str = Field(min_length=1)
    new_password: str = Field(
        min_length=8,
        max_length=72
    )
    confirm_password: str = Field(
        min_length=8,
        max_length=72
    )

    @field_validator(
        "new_password",
        "confirm_password"
    )
    @classmethod
    def validate_password_bytes(cls, value: str):

        return (
            UserRegisterRequest
            .validate_password_bytes(value)
        )

    @model_validator(mode="after")
    def passwords_match(self):

        if (
            self.new_password
            != self.confirm_password
        ):

            raise ValueError(
                "Passwords do not match"
            )

        return self


class MessageResponse(BaseModel):

    message: str


class PasswordResetTokenResponse(BaseModel):

    reset_token: str
    token_type: str = "password_reset"
    expires_in: int
