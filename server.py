from flask import Flask, request, jsonify, render_template
import requests
import json
import socket
import re

app = Flask(__name__)
app.config.from_object('settings')


def get_ip():
    return socket.gethostbyname(app.config.get('CLOUDFLARE_SUBDOMAIN'))

@app.route('/', methods=['get'])
def index():
    ip_octets = re.findall(r'\.?([0-9]+)',get_ip())
    return render_template('form.html', last_ip_octet=ip_octets[-1])

@app.route('/', methods=['post'])
def update():
    ip = request.form.get('ip')

    if not ip:
        return jsonify(result='error', msg='No IP given.'), 400

    req_data = {
        'a': 'rec_edit',
        'tkn': app.config.get('CLOUDFLARE_API_KEY'),
        'email': app.config.get('CLOUDFLARE_EMAIL'),
        'z': app.config.get('CLOUDFLARE_DOMAIN'),
        'id': app.config.get('CLOUDFLARE_RECORD_ID'),
        'type': 'A',
        'name': 'foolio.penano.com',
        'content': ip,
        'ttl': 120
    }

    req = requests.post(app.config.get('CLOUDFLARE_API_URL'), data=req_data)

    if req.status_code != 200:
        return jsonify(**json.loads(req.content)), 403

    result = req.json()

    return jsonify(**result)

@app.route('/ip', methods=['GET'])
def serve_ip():
    ip = get_ip()
    return jsonify(ip=ip)


if __name__ == '__main__':
    app.run('0.0.0.0', port=app.config.get('PORT'))
