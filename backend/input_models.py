from pydantic import BaseModel, Field


class EmailInput(BaseModel):
    """Validated input accepted by the email rewrite endpoint."""

    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1, max_length=20_000)
    target_culture: str = Field(min_length=1, max_length=50)
    tone_emphasis: str | None = Field(default=None, min_length=1, max_length=200)
