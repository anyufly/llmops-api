import json
import logging
import sys

from loguru._colorizer import Colorizer
from loguru._logger import Logger


def init_logger(level: str, debug: bool) -> Logger:
    from loguru import logger

    def serialized(record):
        extra: dict = record["extra"]
        name = extra.pop("name", "")

        subset = {
            "level": record["level"].name,
            "ts": record["time"].timestamp(),
            "proc": record["process"].name,
            "thread": record["thread"].name,
            "file": f"{record['file'].path}:{record['line']}",
            "message": record["message"],
            "payload": extra,
        }

        if name:
            subset["name"] = name

        if record["exception"] is not None:
            subset["error"] = repr(record["exception"])

        return json.dumps(subset)

    def patching(record):
        record["patched_format"] = serialized(record)

    def patching_debug(record):
        extra: dict = record["extra"]
        name = extra.pop("name", "")

        record["patched_format"] = ""

        if name:
            record["patched_format"] += f"<cyan>[{name}] | </cyan>"

        level_color = "green"

        if record["level"].no == logger.level("WARNING").no:
            level_color = "yellow"

        if record["level"].no >= logger.level("ERROR").no:
            level_color = "red"

        record["patched_format"] += (
            f"<cyan>[{record['time']}] | [{record['process'].name}-{record['process'].id}] | [{record['thread'].name}-{record['thread'].id}]</cyan>\n"
            + f"<{level_color}>{record['level']}: {record['message']}</{level_color}>\n"
            + f"<blue>file: {record['file'].path}:{record['line']}</blue>\n"
            + f"<magenta>payload: {json.dumps(record['extra'])}</magenta>\n"
        )

        if record["exception"] is not None:
            record["patched_format"] += f"<red>error:{record['exception']}</red>"
        record["patched_format"] = Colorizer.ansify(record["patched_format"])

    class LoguruHandler(logging.Handler):
        """定义一个handler将python标准logging重定向到loguru输出"""

        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # 获取调用者的帧
            frame, depth = logging.currentframe().f_back, 1

            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).bind(name=record.name).log(
                level, record.getMessage()
            )

    def patch_logger(logger_name: str):
        sub_logger = logging.getLogger(logger_name)
        sub_logger.handlers = [LoguruHandler()]
        sub_logger.setLevel(getattr(logging, "INFO"))
        sub_logger.propagate = False

    def patch_logging():
        logging.basicConfig(handlers=[logging.NullHandler()])
        patch_logger("sqlalchemy.engine.Engine")
        for name in logging.root.manager.loggerDict:
            patch_logger(name)

    patch_logging()
    logger.remove(0)
    logger = logger.patch(patching_debug if debug else patching)
    logger.add(
        sys.stdout,
        format="{patched_format}",
        enqueue=True,
        colorize=True,
        level=level,
    )

    return logger
