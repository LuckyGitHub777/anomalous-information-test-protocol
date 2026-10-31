import threading, unittest
from pathlib import Path
from urllib.request import urlopen
from run_site import Handler, ThreadingHTTPServer
class TestPublicSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.port=cls.server.server_address[1];cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
    def get(self,path='/'):
        with urlopen(f'http://127.0.0.1:{self.port}{path}',timeout=3) as r:return r.status,r.headers,r.read()
    def test_public_home(self):
        status,h,b=self.get('/');self.assertEqual(status,200);self.assertIn(b'Test the claim.',b);self.assertIn(b'Synthetic public demo',b);self.assertIn("connect-src 'none'",h['Content-Security-Policy'])
    def test_assets(self):
        for p in ['/styles.css','/app.js','/favicon.svg']:
            self.assertEqual(self.get(p)[0],200)
if __name__=='__main__':unittest.main()
