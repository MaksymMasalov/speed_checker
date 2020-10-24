import requests

from flask import Flask, jsonify
from flask_restful import reqparse

app = Flask(__name__)


@app.route('/api', methods=['GET', 'POST'])
def speed_counter():
    result_speed = {'download_speed': {}}

    parser = reqparse.RequestParser()
    parser.add_argument('domain', action='append')
    params = parser.parse_args()
    app.logger.info('Parameters: {}'.format(params))
    if params['domain']:
        for domain in params['domain']:
            if 'http' not in domain:
                speed = requests.get('http://'+domain).elapsed.total_seconds()
                result_speed['download_speed'].update({domain: speed})

    return jsonify(result_speed)


if __name__ == '__main__':
    app.run(debug=True)
