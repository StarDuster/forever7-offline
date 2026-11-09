"""Local replacement for the preserved official Android/iOS resource CDN.

This implements patch-list/resource HTTP routes, including single byte ranges.
Game gateway RPC, account/hero state and story progression are NOT implemented.
Client URLs must be patched before it can use this service. Default: loopback.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from tools.preserve_cdn import parse_manifest

ROOT = Path(__file__).resolve().parent


def byte_range(value, size):
    if value is None:
        return 0, size - 1, False
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", value)
    if not match or size <= 0:
        raise ValueError("Unsatisfiable range")
    first, last = match.groups()
    if not first:
        if not last or int(last) <= 0:
            raise ValueError("Unsatisfiable suffix")
        start, end = max(0, size - int(last)), size - 1
    else:
        start, end = int(first), min(int(last), size - 1) if last else size - 1
    if start >= size or start > end:
        raise ValueError("Unsatisfiable range")
    return start, end, True


def make_routes(cdn_root, index=640):
    routes = {}
    for platform in ("android", "ios"):
        prefix = f"patch2.{platform}.{index}"
        manifest = ROOT / f"evidence/{prefix}.version"
        entries = parse_manifest(platform, index, manifest.read_text())
        routes[f"/{prefix}/version"] = manifest
        for entry in entries:
            routes["/" + entry["path"]] = cdn_root / entry["path"]
        for name in (f"patch2_{platform}", f"channel_{platform}", f"minfull_{platform}", f"hotfix_{platform}"):
            source = ROOT / "evidence" / name
            if source.exists():
                routes["/pl/" + name] = source
    return routes


def make_handler(routes):
    patch_directories = {path[:-len('/version')] for path in routes if path.endswith('/version')}
    class Handler(BaseHTTPRequestHandler):
        server_version = "Forever7ResourceMirror/0.1"

        def do_HEAD(self):
            self.serve(False)

        def do_GET(self):
            self.serve(True)

        def serve(self, include_body):
            path = unquote(urlsplit(self.path).path)
            if path in ("/", "/_offline/status"):
                body = json.dumps({"service": "forever7-resource-mirror", "resource_routes": len(routes),
                                   "game_gateway_implemented": False, "runtime_tested": False}, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if include_body:
                    self.wfile.write(body)
                return
            source = routes.get(path)
            if source is None and not include_body and path.rstrip('/') in patch_directories:
                # The native downloader probes its base directory with HEAD
                # before selecting an endpoint. Advertise known mirrors only;
                # real file requests still require an exact preserved route.
                self.send_response(200)
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            if source is None:
                self.send_error(404, "No preserved route")
                return
            try:
                handle = source.open("rb")
            except FileNotFoundError:
                self.send_response(503)
                self.send_header("Retry-After", "5")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            with handle:
                size = source.stat().st_size
                try:
                    first, last, partial = byte_range(self.headers.get("Range"), size)
                except ValueError:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                length = max(0, last - first + 1)
                self.send_response(206 if partial else 200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(length))
                if partial:
                    self.send_header("Content-Range", f"bytes {first}-{last}/{size}")
                self.end_headers()
                if not include_body:
                    return
                handle.seek(first)
                remaining = length
                try:
                    while remaining:
                        block = handle.read(min(1024 * 1024, remaining))
                        if not block:
                            break
                        self.wfile.write(block)
                        remaining -= len(block)
                except (BrokenPipeError, ConnectionResetError):
                    pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8767)
    parser.add_argument("--cdn-root", type=Path, default=ROOT / "originals/cdn")
    parser.add_argument("--index", type=int, default=640)
    parser.add_argument("--overlay-routes", type=Path, help="Private update route map generated by build_update_snapshot.py")
    args = parser.parse_args()
    routes = make_routes(args.cdn_root, args.index)
    if args.overlay_routes:
        overlay = json.loads(args.overlay_routes.read_text())
        for path, filename in overlay.items():
            source = Path(filename).resolve()
            if not path.startswith('/') or not source.is_relative_to(ROOT) or not source.is_file():
                raise ValueError('Invalid private update route')
            routes[path] = source
    server = ThreadingHTTPServer((args.host, args.port), make_handler(routes))
    print(f"Resource mirror: http://{args.host}:{server.server_port}/_offline/status", flush=True)
    print("Game gateway/login/story RPC is not implemented.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
