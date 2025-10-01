from http.server import BaseHTTPRequestHandler, HTTPServer
import json, base64, os
from urllib.parse import urlparse, parse_qs

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'dsa', 'modified_sms_sample.json')

USERS = {'admin': 'password123'}

def check_basic_auth(header_value):
    if not header_value or not header_value.startswith('Basic '):
        return False
    token = header_value.split(' ',1)[1].strip()
    try:
        decoded = base64.b64decode(token).decode('utf-8')
        username, password = decoded.split(':',1)
    except Exception:
        return False
    return USERS.get(username) == password

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE,'r',encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE,'w',encoding='utf-8') as f:
        json.dump(data, f, indent=2)

class SimpleMoMoHandler(BaseHTTPRequestHandler):
    def _unauthorized(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate','Basic realm="MoMo API"')
        self.end_headers()
        self.wfile.write(b'Unauthorized')

    def do_AUTH(self):
        auth = self.headers.get('Authorization')
        return check_basic_auth(auth)

    def _parse_id(self, path):
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'transactions':
            return parts[1]
        return None


    def _send_json(self, code, obj):
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))

    def do_GET(self):
        if not self.do_AUTH():
            return self._unauthorized()
        path = urlparse(self.path).path
        data = load_data()
        if path == '/transactions':
            return self._send_json(200, data)
        tid = self._parse_id(path)
        if tid is not None:
            for t in data:
                if t['Id'] == tid:
                    return self._send_json(200, t)
            return self._send_json(404, {'error': 'Not found'})
        return self._send_json(404, {'error': 'Invalid endpoint'})

    def do_POST(self):
        if not self.do_AUTH():
            return self._unauthorized()
        path = urlparse(self.path).path
        if path != '/transactions':
            return self._send_json(404, {'error': 'Invalid endpoint'})
        
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            obj = json.loads(body.decode('utf-8'))
        except Exception:
            return self._send_json(400, {'error':'Invalid JSON'})
        
        data = load_data()

        
        if data and "Id" in data[-1] and data[-1]["Id"].startswith("TxID"):
            last_num = int(data[-1]["Id"].replace("TxID", ""))
        else:
            last_num = 1542
        obj["Id"] = f"TxID{last_num + 1}"

        data.append(obj)
        save_data(data)
        return self._send_json(201, obj)


    def do_PUT(self):
        if not self.do_AUTH():
            return self._unauthorized()
        path = urlparse(self.path).path
        tid = self._parse_id(path)
        if tid is None:
            return self._send_json(404, {'error':'Invalid endpoint'})
        
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            obj = json.loads(body.decode('utf-8'))
        except Exception:
            return self._send_json(400, {'error':'Invalid JSON'})
        
        data = load_data()
        for i, t in enumerate(data):
            if t['Id'] == tid:
                
                updated = t.copy()
                updated.update(obj)
                updated['Id'] = tid
                data[i] = updated
                save_data(data)
                return self._send_json(200, {"message":'record Updated' +tid})
        
        return self._send_json(404, {'error':'Not found'})


    def do_DELETE(self):
        if not self.do_AUTH():
            return self._unauthorized()
        path = urlparse(self.path).path
        tid = self._parse_id(path)
        if tid is None:
            return self._send_json(404, {'error':'Invalid endpoint'})
        data = load_data()
        for i,t in enumerate(data):
            if t['Id'] == tid:
                removed = data.pop(i)
                save_data(data)
                return self._send_json(200, {'message':'Record Deleted'+tid})
        return self._send_json(404, {'error':'Not found'})

def run(server_class=HTTPServer, handler_class=SimpleMoMoHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
