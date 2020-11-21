import json
import logging
import os
import traceback
from distutils.util import strtobool


class FormatterJSON(logging.Formatter):
    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        if self.usesTime():  # type: ignore
            record.asctime = self.formatTime(record, self.datefmt)
        msg = {
            "name": record.name,
            "levelname": record.levelname,
            "time": "%(asctime)s.%(msecs)dZ"
            % dict(asctime=record.asctime, msecs=record.msecs),
            "aws_request_id": getattr(
                record, "aws_request_id", "00000000-0000-0000-0000-000000000000"
            ),
            "message": record.message,
            "module": record.module,
            "filename": record.filename,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "traceback": {},
            "extra_data": record.__dict__.get("data", {}),
        }
        if record.exc_info:
            exception_data = traceback.format_exc().splitlines()
            msg["traceback"] = exception_data

        return json.dumps(msg, ensure_ascii=False)


class CustomLogger:
    @classmethod
    def getLogger(cls, category_name: str) -> logging.Logger:
        is_offline = strtobool(os.environ.get("IS_OFFLINE", "False"))
        logging.basicConfig()

        if is_offline:
            import coloredlogs

            coloredlogs.install(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")

        else:
            logging.getLogger().handlers[0].setFormatter(
                FormatterJSON(
                    "[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(levelno)s\t%(message)s\n",
                    "%Y-%m-%dT%H:%M:%S",
                )
            )
            for category in ["mangum.lifespan", "mangum.http"]:
                logging.getLogger(category).setLevel(logging.WARNING)

        logger = logging.getLogger(category_name)
        logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))

        return logger

    @classmethod
    def getApplicationLogger(cls) -> logging.Logger:
        return cls.getLogger("application")
