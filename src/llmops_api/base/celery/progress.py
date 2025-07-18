from pydantic import BaseModel, Field

from llmops_api.util.gen_uuid import generate_uuid


class Progress(BaseModel):
    id: str
    total: int = Field(gt=0)


def new_progress(total: int) -> Progress:
    return Progress(id=generate_uuid(), total=total)
