import requests
import threading

from flask_restful import reqparse
from flask import Flask, jsonify, render_template

app = Flask(__name__)
lock = threading.Lock()
result_speed = {'download_speed': {}}


def get_average_latency(link):

    result_speed['download_speed'] = {}

    if 'http' in link:
        speed = requests.get(link, timeout=30).elapsed.total_seconds()
    else:
        speed = requests.get('http://' + link, timeout=30).elapsed.total_seconds()

    with lock:
        result_speed['download_speed'].update(
            {
                link: speed
            }
        )


@app.route('/api/docs')
def get_docs():
    return render_template('swaggerui.html')


@app.route('/api')
def get_api():
    threads = []
    parser = reqparse.RequestParser()
    parser.add_argument('domains', action='append')
    params = parser.parse_args()
    app.logger.info('Parameters: {}'.format(params))
    if params['domains']:
        for domain in params['domains']:
            link_thread = threading.Thread(target=get_average_latency, args=(domain,))
            threads.append(link_thread)
            link_thread.start()
    for thread in threads:
        thread.join()

    return jsonify(result_speed)


if __name__ == '__main__':
    app.run(use_reloader=True, debug=False)
