# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>

import json
import redis

from django.conf import settings


def _publish_message(channel, topic, message_data):
    r = redis.StrictRedis()
    r.publish(channel, json.dumps({'topic': topic, 'data': message_data }))


def broadcast_message(topic, msg):
    _publish_message(settings.DEPLOYMENT_BASENAME + '.broadcast', topic, msg)


def send_message(user, topic, msg):
    _publish_message(settings.DEPLOYMENT_BASENAME + '.user.%d' % user.pk, topic, msg)


def send_message_to_group(group, topic, msg):
    _publish_message(settings.DEPLOYMENT_BASENAME + '.group.%d' % group.pk, topic, msg)
