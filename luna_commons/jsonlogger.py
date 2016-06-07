import copy
import datetime
import json
import logging
from logging.config import dictConfig
import traceback


default_log_config = {
    "version": 1,
    "disable_existing_loggers": True,

    "formatters": {
        "json": {
            "()": "luna_commons.jsonlogger.Formatter",
        },
    },

    "handlers": {
        "json_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },

    "root": {
        "handlers": ["json_console"],
        "level": "INFO",
    },
}


def setup_logging(level=None):
    conf = copy.deepcopy(default_log_config)

    if level is not None:
        conf['root']['level'] = level

    dictConfig(conf)


class Formatter(logging.Formatter):
    @staticmethod
    def serialize_obj(obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M')
        else:
            return str(obj)

    def format(self, record):
        record.message = record.getMessage()  # Combine the message and the args
        if 'exc_info' in record.__dict__ and record.__dict__['exc_info'] is not None and record.__dict__['exc_info'] is not False:
            record.__dict__['exc_info'] = "".join(traceback.format_exception(*record.__dict__['exc_info']))

        record.__dict__['utc_timestamp'] = datetime.datetime.utcnow()

        return json.dumps(record.__dict__, default=self.serialize_obj)
