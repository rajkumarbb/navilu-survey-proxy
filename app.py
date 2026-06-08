import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BHOONIDHI_BASE = 'https://bhoonidhi.nrsc.gov.in/bhoonidhi/api'
BHOONIDHI_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (compatible; SurveyProxy/1.0)',
    'Origin': 'https://bhoonidhi.nrsc.gov.in',
    'Referer': 'https://bhoonidhi.nrsc.gov.in/'
}

def ok(data, status=200):
    r = make_response(jsonify(data), status)
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    r.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return r

@app.route('/')
def index():
    return ok({'status': 'Navilu Survey Proxy', 'version': '2.0'})

@app.route('/ping')
def ping():
    return ok({'status': 'ok'})

@app.route('/bh/login', methods=['GET','POST','OPTIONS'])
def auth():
    if request.method == 'OPTIONS':
        return ok({})
    try:
        payload = request.get_json(silent=True) or {}
        r = requests.post(f'{BHOONIDHI_BASE}/auth/signIn', json=payload, headers=BHOONIDHI_HEADERS, timeout=30)
        try:
            return ok(r.json(), r.status_code)
        except Exception:
            return ok({'error': r.text[:300], 'code': r.status_code}, r.status_code)
    except Exception as e:
        return ok({'error': str(e)}, 500)

@app.route('/stac/search', methods=['POST','OPTIONS'])
def stac_search():
    if request.method == 'OPTIONS':
        return ok({})
    try:
        payload = request.get_json(silent=True) or {}
        token = request.headers.get('Authorization','')
        h = dict(BHOONIDHI_HEADERS)
        if token:
            h['Authorization'] = token
        r = requests.post(f'{BHOONIDHI_BASE}/stac/search', json=payload, headers=h, timeout=60)
        try:
            return ok(r.json(), r.status_code)
        except Exception:
            return ok({'error': r.text[:300], 'code': r.status_code}, r.status_code)
    except Exception as e:
        return ok({'error': str(e)}, 500)

application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
