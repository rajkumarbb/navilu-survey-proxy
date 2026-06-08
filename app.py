import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)

# Allow requests from your GoDaddy site
CORS(app, origins=[
    "http://survey.navilu.in",
    "https://survey.navilu.in",
    "http://navilu.in",
    "https://navilu.in"
])

BHOONIDHI_BASE = 'https://bhoonidhi.nrsc.gov.in/bhoonidhi/api'

BHOONIDHI_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (compatible; SurveyProxy/1.0)',
    'Origin': 'https://bhoonidhi.nrsc.gov.in',
    'Referer': 'https://bhoonidhi.nrsc.gov.in/'
}

@app.route('/')
def index():
    return jsonify({'status': 'Navilu Survey Proxy running', 'version': '1.0'})

@app.route('/ping')
def ping():
    return jsonify({'status': 'ok', 'proxy': 'navilu-survey-proxy', 'bhoonidhi': BHOONIDHI_BASE})

@app.route('/auth/signIn', methods=['POST', 'OPTIONS'])
def auth():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        payload = request.get_json(silent=True) or {}
        r = requests.post(
            f'{BHOONIDHI_BASE}/auth/signIn',
            json=payload,
            headers=BHOONIDHI_HEADERS,
            timeout=30
        )
        try:
            return jsonify(r.json()), r.status_code
        except Exception:
            return jsonify({
                'error': 'Bhoonidhi returned unexpected response',
                'code': r.status_code,
                'body': r.text[:500]
            }), r.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Bhoonidhi timed out. Try again.'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stac/search', methods=['POST', 'OPTIONS'])
def stac_search():
    if request.method == 'OPTIONS':
        return '', 200
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
            return jsonify(r.json()), r.status_code
        except Exception:
            return jsonify({
                'error': 'Bhoonidhi returned unexpected response',
                'code': r.status_code,
                'body': r.text[:500]
            }), r.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Search timed out. Reduce date range.'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<product_id>', methods=['GET', 'OPTIONS'])
def download(product_id):
    if request.method == 'OPTIONS':
        return '', 200
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
            return jsonify(r.json()), r.status_code
        except Exception:
            return jsonify({'error': r.text[:500]}), r.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Gunicorn entry point
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
