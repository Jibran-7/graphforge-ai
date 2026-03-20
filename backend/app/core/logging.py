import logging

_LOGGING_INITIALIZED = False


def init_logging(level: str = "INFO") -> None:
    global _LOGGING_INITIALIZED

    if _LOGGING_INITIALIZED:
        return

    resolved_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(resolved_level)

    handler = logging.StreamHandler()
    handler.setLevel(resolved_level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger.addHandler(handler)
    _LOGGING_INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
