# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>

import datetime
import json
import traceback

from luna_commons.jsonlogger import Formatter


class ContextFilter(object):
    def __init__(self, *args, **kwargs):
        self.context_dict = kwargs

    def filter(self, record):
        record.__dict__.update(self.context_dict)

        # Don't filter out anything
        return 1


class CeleryContextFilter(object):
    def __init__(self, *args, **kwargs):
        try:
            import celery
            self.enable_celery = True
        except ImportError:
            self.enable_celery = False

    def filter(self, record):
        if not self.enable_celery:
            return 1

        try:
            import celery
            if celery.current_task:
                record.__dict__.update({
                    'celery': True,
                    'task_args': celery.current_task.request.args,
                    'task_kwargs': celery.current_task.request.kwargs,
                    'task_name': celery.current_task.name,
                    'task_id': celery.current_task.request.id
                })
        except ImportError:
            self.enable_celery = False

        # Don't filter out anything
        return 1


class SysLogFormatter(Formatter):
    def format(self, record):
        record.message = record.getMessage()  # Combine the message and the args
        if 'exc_info' in record.__dict__ and record.__dict__['exc_info'] is not None and record.__dict__['exc_info'] is not False:
            record.__dict__['exc_info'] = "".join(traceback.format_exception(*record.__dict__['exc_info']))

        record.__dict__['utc_timestamp'] = datetime.datetime.utcnow()
        data = record.__dict__

        deployment_name = data.get('DEPLOYMENT_BASENAME', None)
        pid = data.get('process', None)
        json_data = json.dumps(data, default=self.serialize_obj)

        if deployment_name is not None:
            process_name = 'django-%s' % deployment_name
        else:
            process_name = 'django'

        if pid is not None:
            serialized_value = '%s[%d]: %s' % (process_name, pid, json_data)
        else:
            serialized_value = '%s: %s' % (process_name, json_data)

        return serialized_value
