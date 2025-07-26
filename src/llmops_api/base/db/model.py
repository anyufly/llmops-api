import datetime
from typing import Any, Dict, List, Optional, Set, Type, cast

import stringcase
from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from llmops_api.base.view.relation import Relation
from llmops_api.util.sha256_with_salt import sha256_with_salt, verify_hashed


def is_sqlalchemy_model_list(list: List[Any]) -> bool:
    found = False
    for item in list:
        if not isinstance(item, Base):
            found = True
            break
    return not found


class Base(AsyncAttrs, DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return f"t_{stringcase.snakecase(cls.__name__)}"

    def to_pydantic(
        self,
        pydantic_model: Type[BaseModel],
        *,
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
    ):
        orm_attrs = self._get_attributes()

        filtered_attrs = self._filter_attributes(orm_attrs, include=include, exclude=exclude)

        attrs = {}

        for name, info in pydantic_model.model_fields.items():
            if name in filtered_attrs.keys():
                value = filtered_attrs[name]

                if isinstance(value, Base):
                    for meta in info.metadata:
                        if isinstance(meta, Relation):
                            if meta.pydantic_model == "self":
                                meta.pydantic_model = pydantic_model

                            pydantic_value = value.to_pydantic(
                                meta.pydantic_model,
                                include=meta.include,
                                exclude=meta.exclude,
                            )
                            attrs[name] = pydantic_value

                    continue
                elif isinstance(value, list):
                    if is_sqlalchemy_model_list(value):
                        attrs[name] = []
                        for item in value:
                            for meta in info.metadata:
                                if isinstance(meta, Relation):
                                    if meta.pydantic_model == "self":
                                        meta.pydantic_model = pydantic_model
                                    pydantic_value = item.to_pydantic(
                                        meta.pydantic_model,
                                        include=meta.include,
                                        exclude=meta.exclude,
                                    )
                                    attrs[name].append(pydantic_value)
                        continue

                attrs[name] = value

        return pydantic_model(**attrs)

    def _get_attributes(self):
        inspector = inspect(self)
        columns = inspector.mapper.columns
        attrs = {c.key: getattr(self, c.key) for c in columns}
        relationships = inspector.mapper.relationships

        # 添加关系属性
        for rel in relationships:
            # 仅处理已加载的关系
            if rel.key in inspector.unloaded:
                continue
            attrs[rel.key] = getattr(self, rel.key)

        return attrs

    @staticmethod
    def _filter_attributes(
        attrs: Dict[str, Any],
        include: Optional[Set[str]] = None,
        exclude: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """根据include/exclude过滤属性字典"""
        if include:
            return {k: v for k, v in attrs.items() if k in include}
        if exclude:
            return {k: v for k, v in attrs.items() if k not in exclude}
        return attrs


class AutoIncrementID:
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )


class OperateRecord:
    create_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    create_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("t_user.id"),
        nullable=True,
        default=None,
    )

    @declared_attr
    def creator(cls) -> Mapped[Optional["User"]]:
        table_name = cls.__tablename__
        return relationship(
            foreign_keys=[cls.create_by],
            primaryjoin=f"and_(remote(t_user.c.id) == {table_name}.c.create_by , remote(t_user.c.delete_at).is_(None))",
        )

    update_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, onupdate=func.now()
    )

    update_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("t_user.id"),
        nullable=True,
        default=None,
    )

    @declared_attr
    def updator(cls) -> Mapped[Optional["User"]]:
        table_name = cls.__tablename__
        return relationship(
            foreign_keys=[cls.update_by],
            primaryjoin=f"and_(remote(t_user.c.id) == {table_name}.c.update_by , remote(t_user.c.delete_at).is_(None),)",
        )


class SoftDelete:
    delete_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    delete_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("t_user.id"),
        nullable=True,
        default=None,
    )


class User(Base, AutoIncrementID, OperateRecord, SoftDelete):
    username: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        default="",
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="",
    )

    password: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    password_salt: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    def __init__(self, **kw: Any):
        password = kw.get("password", None)
        if password:
            salt, hashed_password = sha256_with_salt(password)
            kw.update({"password": hashed_password, "password_salt": salt})
        super().__init__(**kw)

    def set_password(self, password: str):
        salt, hashed_password = sha256_with_salt(password)
        self.password = hashed_password
        self.password_salt = salt

    def check_password(self, password: str) -> bool:
        return verify_hashed(password, self.password_salt, self.password)


class CasbinRule(Base, AutoIncrementID):
    __table_args__ = (UniqueConstraint("ptype", "v0", "v1", "v2", "v3", "v4", "v5"),)

    @declared_attr
    def __tablename__(cls) -> str:
        return "casbin_rule"

    ptype: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    v0: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    v1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    v2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    v3: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    v4: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    v5: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if v is None:
                break
            arr.append(v)
        return ", ".join(cast(List[str], arr))

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))
