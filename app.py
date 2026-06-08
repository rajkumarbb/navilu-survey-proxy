import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

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
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'proxy': 'survey.navilu.in', 'bhoonidhi': BHOONIDHI_BASE})

@app.route('/auth/signIn', methods=['POST'])
def auth():
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
            return jsonify({'error': 'Non-JSON from Bhoonidhi', 'code': r.status_code, 'body': r.text[:500]}), r.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Bhoonidhi timed out'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stac/search', methods=['POST'])
def stac_search():
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
            return jsonify({'error': 'Non-JSON from Bhoonidhi', 'code': r.status_code, 'body': r.text[:500]}), r.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Search timed out'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<product_id>', methods=['GET'])
def download(product_id):
    try:
        token = request.headers.get('Authorization', '')
        headers = dict(BHOONIDHI_HEADERS)
        if token:
            headers['Authorization'] = token
        r = requests.get(f'{BHOONIDHI_BASE}/download/{product_id}', headers=headers, timeout=60)
        try:
            return jsonify(r.json()), r.status_code
        except Exception:
            return jsonify({'error': r.text[:500]}), r.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

application = app

if __name__ == '__main__':
    app.run(debug=False)
