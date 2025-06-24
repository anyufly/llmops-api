from typing import List, Optional

from sqlalchemy import Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llmops_api.base.db.model import AutoIncrementID, Base, OperateRecord, SoftDelete
from llmops_api.enum.menu import ActionMethod, MenuType


class Menu(Base, AutoIncrementID, OperateRecord, SoftDelete):
    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    path: Mapped[str] = mapped_column(String(200), nullable=False)

    icon: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )

    icon_filled: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )

    menu_type: Mapped[MenuType] = mapped_column(
        Enum(MenuType),
        nullable=False,
    )

    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("t_menu.id"),
        nullable=True,
        default=None,
    )

    parent: Mapped[Optional["Menu"]] = relationship(
        foreign_keys=[parent_id],
        back_populates="children",
        primaryjoin="and_(remote(Menu.id) == Menu.parent_id , remote(Menu.delete_at).is_(None))",
    )

    children: Mapped[List["Menu"]] = relationship(
        back_populates="parent",
        primaryjoin="and_(Menu.id == remote(Menu.parent_id) , remote(Menu.delete_at).is_(None))",
    )

    actions: Mapped[List["Action"]] = relationship(
        back_populates="menu",
        primaryjoin="remote(Action.menu_id) == Menu.id",
    )


class Action(Base, AutoIncrementID, OperateRecord):
    __table_args__ = (UniqueConstraint("path", "method"),)

    menu_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("t_menu.id"),
        nullable=True,
        default=None,
    )

    menu: Mapped["Menu"] = relationship(
        foreign_keys=[menu_id],
        back_populates="actions",
        primaryjoin="and_(Action.menu_id == remote(Menu.id) , remote(Menu.delete_at).is_(None))",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    path: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    method: Mapped[ActionMethod] = mapped_column(
        Enum(ActionMethod),
        nullable=False,
    )
