from typing import List, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llmops_api.base.db.model import AutoIncrementID, Base, OperateRecord, SoftDelete
from llmops_api.enum.plugins import PluginType


class PluginProvider(Base, AutoIncrementID, OperateRecord, SoftDelete):
    """
    插件提供商
    """

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    tools: Mapped[List["Plugin"]] = relationship(back_populates="provider")


class Plugin(Base, AutoIncrementID, OperateRecord, SoftDelete):
    """
    插件
    """

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        default="",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    plugin_type: Mapped[PluginType] = mapped_column(
        Enum(PluginType),
        nullable=False,
    )

    provider_id: Mapped[Integer] = mapped_column(
        Integer,
        ForeignKey("t_plugin_provider.id"),
        nullable=False,
    )

    config: Mapped[Optional["CustomPluginConfig"]] = relationship(
        back_populates="plugin",
    )

    provider: Mapped[PluginProvider] = relationship(
        back_populates="tools",
        foreign_keys=[
            provider_id,
        ],
    )

    args: Mapped[List["PluginArgs"]] = relationship(back_populates="plugin")
    tags: Mapped[List["PluginTags"]] = relationship(
        secondary="PluginTagAssociation",
        back_populates="plugins",
    )


class PluginTags(Base, AutoIncrementID, OperateRecord):
    """
    插件标签
    """

    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    plugins: Mapped[List["Plugin"]] = relationship(
        secondary="PluginTagAssociation",
        back_populates="tags",
    )


class PluginTagAssociation(Base, AutoIncrementID, OperateRecord):
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_plugin_tags.id"),
        nullable=False,
    )

    plugin_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_plugin.id"), nullable=False)


class PluginArgs(Base, AutoIncrementID, OperateRecord):
    """
    插件参数
    """

    plugin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_plugin.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    arg_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    arg_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    plugin: Mapped["Plugin"] = relationship(
        foreign_keys=[plugin_id],
        back_populates="args",
    )


class CustomPluginConfig(Base, AutoIncrementID, OperateRecord):
    """
    自定义（API）插件配置
    """

    openapi_schema: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    headers: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        default=None,
        nullable=True,
    )
    plugin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_plugin.id"),
        nullable=False,
    )
    plugin: Mapped["Plugin"] = relationship(foreign_keys=[plugin_id], back_populates="config")
    __table_args__ = (
        # 创建 GIN 索引加速 JSONB 查询
        Index("idx_openapi_schema", openapi_schema, postgresql_using="gin"),
        Index("idx_headers", headers, postgresql_using="gin"),
    )
