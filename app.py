from flask import Flask, render_template, jsonify, send_from_directory
from proxy_runner import start_mitm
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('main.html', now=datetime.now().strftime('%H:%M:%S'))

@app.route('/customize')
def customize_page():
    return render_template('customize.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/start')
async def start_star_hybrid():
    await start_mitm()
    return jsonify({"status": "Proxy started"})


@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

if __name__ == '__main__':
    app.run(debug=True)