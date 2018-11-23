from gevent.pywsgi import WSGIServer
from app import create_app

print("식품 정보 version 0.0.1")
print("gevent server started at http://localhost:5000")
http_server = WSGIServer(('0.0.0.0', 5000), create_app())
http_server.serve_forever()