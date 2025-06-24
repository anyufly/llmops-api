from fastapi import FastAPI

from llmops_api.api.action import router as actionRouter
from llmops_api.api.auth import router as authRouter
from llmops_api.api.menu import router as menuRouter
from llmops_api.api.menu_action import router as menuActionRouter
from llmops_api.api.permissisons import router as permissionsRouter
from llmops_api.api.role import router as roleRouter
from llmops_api.api.user import router as userRouter

routers = [
    userRouter,
    menuRouter,
    authRouter,
    actionRouter,
    menuActionRouter,
    roleRouter,
    permissionsRouter,
]


def add_routers(app: FastAPI):
    for router in routers:
        app.include_router(router)
