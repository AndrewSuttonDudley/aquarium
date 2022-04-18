from flask import Flask
import json


flask = Flask('aquarium')
logger = flask.logger


def load_json_file(filename) -> dict:
    with open(filename) as json_file:
        config = json.load(json_file)
        logger.info(f'JSON ({filename}) loaded')
        return config
