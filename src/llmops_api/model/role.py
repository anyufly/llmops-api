from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from llmops_api.base.db.model import AutoIncrementID, Base, OperateRecord, SoftDelete


class Role(Base, AutoIncrementID, OperateRecord, SoftDelete):
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
