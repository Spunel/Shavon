from pydantic import BaseModel, field_validator


class LoginForm(BaseModel):
    """ Form for user login.
    """
    email: str
    password: str
    require_captcha: bool
    captcha: str | None

    @field_validator("captcha")
    @classmethod
    def validate_captcha(cls, captcha: str, values: dict) -> str:
        if values.data.get('require_captcha', False):
            print("Captcha is required.")
            if captcha is None or len(captcha.strip()) <= 0:
                raise ValueError("Required")
        return captcha

