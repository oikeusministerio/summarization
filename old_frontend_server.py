
from flask import Flask, jsonify,request, send_from_directory, send_file
import logging

#inner imports

app = Flask(__name__, static_url_path='')

UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/node_modules/<path:path>')
def send_node_modules(path):
    return send_from_directory('static/node_modules', path)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
#    header['Access-Control-Allow-Methods'] = 'POST, GET'
    header['Access-Control-Allow-Headers'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0', port=7000)