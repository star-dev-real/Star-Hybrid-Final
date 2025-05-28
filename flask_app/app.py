from flask import Flask, render_template, jsonify
from proxy_runner import start_mitm
from proxy_logic import get_logs 

app = Flask(__name__)

@app.route('/')
def main_page():
    from datetime import datetime
    return render_template('main.html', now=datetime.now().strftime('%H:%M:%S'))

@app.route('/start')
def start_star_hybrid():
    start_mitm()
    return jsonify({"status": "Proxy started"})

@app.route('/logs')
def get_log_data():
    return jsonify(get_logs())

if __name__ == '__main__':
    app.run(debug=True)
