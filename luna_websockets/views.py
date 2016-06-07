# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>

from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class GetSubscribedChannels(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        channels = [
            settings.DEPLOYMENT_BASENAME + '.broadcast',
            settings.DEPLOYMENT_BASENAME + '.user.%d' % request.user.pk
        ]

        for g in request.user.groups.all():
            channels.append(settings.DEPLOYMENT_BASENAME + '.group.%d' % g.pk)

        return Response({'channels': channels})
