import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests

app = Flask(__name__)

# Permissive CORS — allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})

BHOONIDHI_BASE = 'https://bhoonidhi.nrsc.gov.in/bhoonidhi/api'

BHOONIDHI_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (compatible; SurveyProxy/1.0)',
    'Origin': 'https://bhoonidhi.nrsc.gov.in',
    'Referer': 'https://bhoonidhi.nrsc.gov.in/'
}

def cors_response(data, status=200):
    resp = make_response(jsonify(data), status)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return resp

@app.route('/')
def index():
    return cors_response({'status': 'Navilu Survey Proxy', 'version': '1.0'})

@app.route('/ping', methods=['GET', 'OPTIONS'])
def ping():
    return cors_response({'status': 'ok', 'proxy': 'navilu-survey-proxy'})

@app.route('/auth/signIn', methods=['POST', 'GET', 'OPTIONS'])
def auth():
    if request.method == 'OPTIONS':
        resp = make_response('', 200)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return resp
    try:
        payload = request.get_json(silent=True) or {}
        r = requests.post(
            f'{BHOONIDHI_BASE}/auth/signIn',
            json=payload,
            headers=BHOONIDHI_HEADERS,
            timeout=30
        )
        try:
            return cors_response(r.json(), r.status_code)
        except Exception:
            return cors_response({'error': r.text[:500], 'code': r.status_code}, r.status_code)
    except requests.exceptions.Timeout:
        return cors_response({'error': 'Bhoonidhi timed out'}, 504)
    except Exception as e:
        return cors_response({'error': str(e)}, 500)

@app.route('/stac/search', methods=['POST', 'OPTIONS'])
def stac_search():
    if request.method == 'OPTIONS':
        resp = make_response('', 200)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return resp
    try:
        payload = request.get_json(silent=True) or {}
        token = request.headers.get('Authorization', '')
        headers = dict(BHOONIDHI_HEADERS)
        if token:
            headers['Authorization'] = token
        r = requests.post(
            f'{BHOONIDHI_BASE}/stac/search',
            json=payload,
            headers=headers,
            timeout=60
        )
        try:
            return cors_response(r.json(), r.status_code)
        except Exception:
            return cors_response({'error': r.text[:500], 'code': r.status_code}, r.status_code)
    except requests.exceptions.Timeout:
        return cors_response({'error': 'Search timed out'}, 504)
    except Exception as e:
        return cors_response({'error': str(e)}, 500)

@app.route('/download/<product_id>', methods=['GET', 'OPTIONS'])
def download(product_id):
    if request.method == 'OPTIONS':
        resp = make_response('', 200)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        return resp
    try:
        token = request.headers.get('Authorization', '')
        headers = dict(BHOONIDHI_HEADERS)
        if token:
            headers['Authorization'] = token
        r = requests.get(
            f'{BHOONIDHI_BASE}/download/{product_id}',
            headers=headers,
            timeout=60
        )
        try:
            return cors_response(r.json(), r.status_code)
        except Exception:
            return cors_response({'error': r.text[:500]}, r.status_code)
    except Exception as e:
        return cors_response({'error': str(e)}, 500)

# Gunicorn/WSGI entry point
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
