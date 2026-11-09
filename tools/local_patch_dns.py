"""Opt-in direct TLS patch mirror and restricted DNS for a test phone.

Unlike an HTTP proxy, this can test clients which connect directly. It does not
disable certificate validation or decrypt an iOS executable. Bind low ports as
root, then drop to the invoking user's identity before handling requests.
Only the two patch names are answered locally; other DNS questions are relayed
to the specified existing resolver without logging or inspecting their data.
Stop the service and restore the phone's DNS settings after testing.
"""
import argparse
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import os
from pathlib import Path
import signal
import re
import socket
import socketserver
import ssl
import threading

from dnslib import A, DNSRecord, QTYPE, RCODE, RR

PATCH_HOSTS = frozenset(('g58.update.netease.com', 'g58.gph.netease.com'))
EVENT_LOG = None
LIVE_CONFIG = None


def live_config():
    if LIVE_CONFIG is None:
        return {}
    config = json.loads(Path(LIVE_CONFIG).read_text())
    for host in config.get('hosts', ()):
        if host != 'mbdl.update.netease.com' and not re.fullmatch(r'g58(?:-\d+)?\.(?:update|gph|gdl)\.netease\.com', host):
            raise ValueError('Only this game CDN names may be configured')
    if 'upstream_dns' in config:
        ipaddress.IPv4Address(config['upstream_dns'])
    return config


def patch_hosts():
    config = live_config()
    if not config.get('enabled', True):
        return frozenset()
    return PATCH_HOSTS | frozenset(config.get('hosts', ()))


def event_log(message):
    print(message, flush=True)
    if EVENT_LOG:
        with open(EVENT_LOG, 'a') as handle:
            handle.write(message + '\n')


def dns_answer(packet, address, upstream):
    query = DNSRecord.parse(packet)
    if query.header.qr or query.header.opcode or len(query.questions) != 1:
        raise ValueError('Expected one standard DNS question')
    question = query.questions[0]
    name = str(question.qname).rstrip('.').lower()
    if name in patch_hosts():
        answer = query.reply()
        if question.qtype in (QTYPE.A, QTYPE.ANY):
            answer.add_answer(RR(question.qname, QTYPE.A, ttl=5, rdata=A(address)))
        # Empty AAAA/HTTPS responses avoid sending this test to a public IPv6
        # or alternative service endpoint. No wildcard DNS rewriting.
        event_log('Local patch DNS: %s %s' % (name, QTYPE.get(question.qtype)))
        return answer.pack()
    return upstream(packet)


def relay_dns(packet, resolver):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(4)
        sock.connect((resolver, 53))
        sock.send(packet)
        response = sock.recv(65535)
    if response[:2] != packet[:2]:
        raise ValueError('DNS transaction mismatch')
    return response


class RestrictedUDP(socketserver.ThreadingUDPServer):
    daemon_threads = True

    def verify_request(self, request, address):
        return address[0] in self.allowed


class DNSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        packet, sock = self.request
        try:
            upstream = live_config().get('upstream_dns', self.server.upstream)
            response = dns_answer(packet, self.server.bind_address,
                                  lambda data: relay_dns(data, upstream))
        except Exception:
            try:
                response = DNSRecord.parse(packet).reply()
                response.header.rcode = RCODE.SERVFAIL
                response = response.pack()
            except Exception:
                return
        sock.sendto(response, self.client_address)


class RestrictedHTTPS(ThreadingHTTPServer):
    daemon_threads = True

    def get_request(self):
        # Reject other peers before TLS negotiation, and prevent an idle peer
        # from blocking the accept loop indefinitely.
        while True:
            connection, address = self.socket.accept()
            if address[0] not in self.allowed:
                connection.close()
                continue
            connection.settimeout(10)
            try:
                self.tls.load_cert_chain(self.cert_path)
                connection = self.tls.wrap_socket(connection, server_side=True)
                event_log('Local patch TLS: accepted')
                return connection, address
            except OSError as error:
                event_log('Patch TLS failed: %s' % error)
                connection.close()


class PatchHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        self.serve_patch()

    def do_HEAD(self):
        self.serve_patch()

    def serve_patch(self):
        host = self.headers.get('Host', '').split(':')[0].lower()
        config = live_config()
        local_ip_host = host == self.server.server_address[0] and self.path.startswith('/patch2.ios.')
        if (host not in patch_hosts() and not local_ip_host) or not self.path.startswith('/') or self.path.startswith('//'):
            self.send_error(403)
            return
        if host == 'mbdl.update.netease.com' and self.path.split('?')[0] != '/g58.mbdl':
            # This is a shared public SDK configuration host. Only this game's
            # config is changed. Other public .mbdl files retain their official
            # response, using verified upstream TLS. No cookies/auth forwarded.
            if not re.fullmatch(r'/[A-Za-z0-9_-]+\.mbdl(?:\?.*)?', self.path):
                self.send_error(403)
                return
            upstream = http.client.HTTPSConnection('mbdl.update.netease.com', timeout=30)
            log_transfer = False
        else:
            upstream = http.client.HTTPConnection('127.0.0.1', self.server.mirror_port, timeout=30)
            log_transfer = True
        try:
            headers = {key: self.headers[key] for key in ('Range', 'If-Range') if key in self.headers}
            upstream.request(self.command, self.path, headers=headers)
            response = upstream.getresponse()
            self.send_response(response.status)
            for key in ('Content-Type', 'Content-Length', 'Content-Range', 'Accept-Ranges', 'ETag'):
                value = response.getheader(key)
                if value is not None:
                    self.send_header(key, value)
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            if log_transfer:
                event_log('Local patch HTTPS: %s %s %s' % (self.command, self.path, response.status))
            if self.command != 'HEAD':
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except (OSError, http.client.HTTPException) as error:
            event_log('Patch transfer failed: %s' % type(error).__name__)
            self.close_connection = True
        finally:
            upstream.close()


def main():
    global EVENT_LOG, LIVE_CONFIG
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', required=True, type=ipaddress.IPv4Address)
    parser.add_argument('--client', required=True, type=ipaddress.IPv4Address)
    parser.add_argument('--upstream-dns', required=True, type=ipaddress.IPv4Address)
    parser.add_argument('--cert', required=True, type=Path, help='Leaf certificate and private key PEM')
    parser.add_argument('--dns-port', type=int, default=53)
    parser.add_argument('--https-port', type=int, default=443)
    parser.add_argument('--mirror-port', type=int, default=8767)
    parser.add_argument('--event-log', type=Path, help='Patch-only events, no unrelated DNS query logs')
    parser.add_argument('--config', type=Path, help='Reloadable exact game CDN hosts and upstream DNS')
    args = parser.parse_args()
    address = str(args.bind)
    if not args.bind.is_private or not args.client.is_private:
        parser.error('Use a private LAN test address')
    LIVE_CONFIG = str(args.config) if args.config else None
    live_config()
    try:
        response = DNSRecord.parse(relay_dns(DNSRecord.question('httpdns.nie.netease.com').pack(), str(args.upstream_dns)))
        if response.header.rcode not in (RCODE.NOERROR, RCODE.NXDOMAIN):
            raise ValueError('Upstream DNS returned an error')
    except (OSError, ValueError) as error:
        parser.error('Upstream DNS preflight failed: %s' % error)
    allowed = frozenset((str(args.client), address, '127.0.0.1'))
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.load_cert_chain(args.cert)
    tls.minimum_version = ssl.TLSVersion.TLSv1_2
    dns = RestrictedUDP((address, args.dns_port), DNSHandler)
    dns.allowed, dns.bind_address, dns.upstream = allowed, address, str(args.upstream_dns)
    https = RestrictedHTTPS((address, args.https_port), PatchHandler)
    https.allowed, https.tls, https.mirror_port = allowed, tls, args.mirror_port
    https.cert_path = str(args.cert)
    if os.geteuid() == 0:
        if not os.environ.get('SUDO_UID') or int(os.environ['SUDO_UID']) == 0:
            parser.error('Run through sudo as a normal user; the service must drop privileges')
        os.setgroups([])
        os.setgid(int(os.environ['SUDO_GID']))
        os.setuid(int(os.environ['SUDO_UID']))
    EVENT_LOG = str(args.event_log) if args.event_log else None
    event_log('Patch DNS %s:%s; TLS %s:%s; UID %s; allowed clients %s' % (
        address, args.dns_port, address, args.https_port, os.geteuid(), ','.join(sorted(allowed))))
    threading.Thread(target=dns.serve_forever, daemon=True).start()
    def stop_service(*_):
        raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM, stop_service)
    try:
        https.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        dns.shutdown()
        dns.server_close()
        https.server_close()


if __name__ == '__main__':
    main()
