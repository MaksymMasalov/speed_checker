import requests
import threading

from flask import Flask, jsonify
from flask_restplus import Api, Resource, reqparse

flask_app = Flask(__name__)

app = Api(app=flask_app,
          version="1.0",
          title="Speed checker",
          description="Application for checking the speed of loading domains.")

name_space = app.namespace('api-domains', description='Manage domains')

lock = threading.Lock()

result_speed = {'download_speed': {}}


def get_average_latency(link):
    speed = requests.get('http://' + link).elapsed.total_seconds()
    with lock:
        result_speed['download_speed'].update(
            {
                link: speed
            }
        )


@name_space.route("/")
class MainClass(Resource):

    @app.doc(responses={200: "OK", 400: "Invalid Argument", 500: "Mapping Key Error"},
             params={"domains": {"description": "Specify the name of domain",
                                 "in": "query",
                                 "type": "array",
                                 "items": {"type": "string"}
                                 }})
    def get(self):
        try:
            threads = []
            parser = reqparse.RequestParser()
            parser.add_argument('domains')
            params = parser.parse_args()
            flask_app.logger.info('Parameters: {}'.format(params))
            if params['domains']:
                for domain in params['domains'].split(','):
                    link_thread = threading.Thread(target=get_average_latency, args=(domain,))
                    threads.append(link_thread)
                    link_thread.start()
            for thread in threads:
                thread.join()

            return jsonify(result_speed)

        except KeyError as e:
            name_space.abort(500, e.__doc__, status="Could not retrieve information", statusCode="500")
        except Exception as e:
            name_space.abort(400, e.__doc__, status="Could not retrieve information", statusCode="400")


if __name__ == '__main__':
    flask_app.run(debug=True)
