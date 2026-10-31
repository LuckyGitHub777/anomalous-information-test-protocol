from __future__ import annotations
import argparse, threading, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SITE=ROOT/'site'

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(SITE),**kwargs)
    def log_message(self,fmt,*args): return
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Permissions-Policy','camera=(), microphone=(), geolocation=(), payment=(), usb=()')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; font-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        super().end_headers()

def main():
    ap=argparse.ArgumentParser(description='Preview the static AITP public web experience on loopback only.')
    ap.add_argument('--host',default='127.0.0.1');ap.add_argument('--port',type=int,default=8787);ap.add_argument('--no-browser',action='store_true');args=ap.parse_args()
    if args.host not in {'127.0.0.1','localhost','::1'}: raise SystemExit('STOP — public-site preview binds only to loopback.')
    srv=ThreadingHTTPServer((args.host,args.port),Handler);url=f'http://127.0.0.1:{args.port}/'
    print('AITP PUBLIC WEB PREVIEW');print('Synthetic demo · no telemetry · loopback only');print('Open:',url)
    if not args.no_browser: threading.Timer(.3,lambda:webbrowser.open(url)).start()
    try:srv.serve_forever()
    except KeyboardInterrupt:pass
    finally:srv.server_close()
if __name__=='__main__':main()
