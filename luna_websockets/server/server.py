import grp
import json
import os

from django.core.urlresolvers import reverse

import tornado.gen
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
from tornado.netutil import bind_unix_socket
import tornado.web
import sockjs.tornado
import tornadoredis
import tornadoredis.pubsub

import logging
logging.getLogger().setLevel(logging.DEBUG)

subscriber = tornadoredis.pubsub.SockJSSubscriber(tornadoredis.Client())


class BrokerConnection(sockjs.tornado.SockJSConnection):
    def on_open(self, info):
        logging.info('Incoming client from %s' % info.ip)
        self.channels = []

    def on_message(self, msg):
        msg_data = json.loads(msg)

        cmd = msg_data.get('cmd', None)
        if cmd == 'AUTH':
            self.auth(msg_data)
        elif cmd == 'DEAUTH':
            self.deauth()

    @tornado.gen.coroutine
    def auth(self, msg):
        client = tornado.httpclient.AsyncHTTPClient()
        url = self.subscribed_channels_url
        response = yield tornado.gen.Task(client.fetch, url, headers={'Authorization': 'Token %s' % msg['token']})
        if response.code != 200:
            print('Bad request: Got response code: %d' % response.code)
        else:
            channels = json.loads(response.body.decode('UTF-8'))['channels']
            subscriber.subscribe(channels, self)
            self.channels += channels

    def deauth(self):
        for chan in self.channels:
            subscriber.unsubscribe(chan, self)


def run_server(
        django_host='http://127.0.0.1:8000',
        listen_address='0.0.0.0',
        listen_port=22000,
        unix_socket=None,
        socket_mode=0o600,
        socket_group=None):

    subscribed_channels_url = django_host + reverse('luna_websockets_channels')
    BrokerConnection.subscribed_channels_url = subscribed_channels_url

    BrokerRouter = sockjs.tornado.SockJSRouter(BrokerConnection, '/ws')

    app = tornado.web.Application(BrokerRouter.urls)

    if unix_socket:
        server = tornado.httpserver.HTTPServer(app)
        socket = bind_unix_socket(unix_socket, mode=socket_mode)
        if socket_group is not None:
            gid = grp.getgrnam(socket_group).gr_gid
            os.chown(unix_socket, -1, gid)

        server.add_socket(socket)
        logging.info('Listening on %s' % unix_socket)
    else:
        app.listen(listen_port, address=listen_address)
        logging.info('Listening on %s:%d' % (listen_address, listen_port))

    tornado.ioloop.IOLoop.instance().start()
