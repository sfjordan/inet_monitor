from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import socket, os

class MyHandler(SimpleHTTPRequestHandler):
  def do_GET(self):
    try:
      if self.path == '/ip':
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('Your IP address is %s' % self.client_address[0])
        return
      if self.path == '/ping':
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<h>PONG</p>')
        return
      if self.path == '/network':
        speed_img = "speed_data.png"
        pktloss_img = "pktloss_data.png"
        lat_img = "lat_data.png"
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<img src='+speed_img+'/>')
        self.wfile.write('<img src='+pktloss_img+'/>')
        self.wfile.write('<img src='+lat_img+'/>')
        return
      if self.path == '/speed':
        img = os.sep+'home'+os.sep+'sfjordan'+os.sep+\
            'speed_data.png'
        f = open(img)
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.send_headers()
        self.wfile.write(f.read())
        f.close()
        return
      if self.path == '/pktloss':
        img = os.sep+'home'+os.sep+'sfjordan'+os.sep+\
            'pktloss_data.png'
        f = open(img)
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(f.read())
        f.close()
        return
      else:
        return SimpleHTTPRequestHandler.do_GET(self)
    except IOError:
      self.send_error(404, 'File Not Found: %s' % self.path)

class HTTPServerV6(HTTPServer):
  address_family = socket.AF_INET6

def main():
  server = HTTPServerV6(('::', 80), MyHandler)
  server.serve_forever()

if __name__ == '__main__':
  main()



