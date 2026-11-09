"""mitmproxy addon: redirect only the two game's patch hosts to loopback.

Launch with allow_hosts restricted to these exact hosts and streaming enabled.
It does not alter login traffic or forward an update to official infrastructure.
Installing a local CA/proxy on a phone is a separate, user-approved action.
"""
import os
from mitmproxy import http

PATCH_HOSTS = frozenset(['g58.update.netease.com', 'g58.gph.netease.com'])
CLIENT_IPS = frozenset(['127.0.0.1', '::1'] +
                      os.environ.get('FOREVER7_PROXY_CLIENT_IPS', '').split(','))


def client_connected(client):
    if client.peername[0] not in CLIENT_IPS:
        client.error = 'Client is not enabled for this local development proxy'


def request(flow):
    if flow.request.host.lower() not in PATCH_HOSTS:
        return
    flow.metadata['forever7_patch_path'] = flow.request.path
    if flow.request.method not in ('GET', 'HEAD'):
        flow.response = http.Response.make(405, b'Patch mirror accepts GET/HEAD only')
        return
    flow.request.scheme = 'http'
    flow.request.host = '127.0.0.1'
    flow.request.port = 8767


def response(flow):
    path = flow.metadata.get('forever7_patch_path', '')
    if path.startswith('/pl/patch2_'):
        flow.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        flow.response.headers['Cache-Control'] = 'no-store'
