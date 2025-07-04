from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llmops_api.base.casbin import enforcer
from llmops_api.base.container import init_container
from llmops_api.base.exception import error_handlers
from llmops_api.base.response import responses
from llmops_api.base.routers import add_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = app.container.logger()  # type: ignore
    db = app.container.db()  # type: ignore
    casbin_enforcer: enforcer.CasbinEnforcer = await app.container.casbin_enforcer()  # type: ignore
    redis = app.container.redis()  # type: ignore

    yield
    logger.info("start close db engine...")
    await db.close()
    logger.info("db engine closed...")
    casbin_enforcer.watcher.stop_subscribe_msg()

    await redis.close()


container = init_container()

app = FastAPI(
    root_path="/api/v1",
    exception_handlers=error_handlers,
    responses=responses,
    title="llmops-api",
    description="LLM大语言模型应用编排系统后端API",
    lifespan=lifespan,
    debug=container.config().env.debug_mode,
)


app.container = container  # type: ignore

app.add_middleware(
    CORSMiddleware,
    **container.config().cors.model_dump(
        include={
            "allow_origins",
            "allow_credentials",
            "allow_methods",
            "allow_headers",
            "expose_headers",
            "max_age",
        }
    ),
)

# 添加路由
add_routers(app)

# uvicorn src.llmops_api.main:app --host 0.0.0.0 --port 8080 --workers 8
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
