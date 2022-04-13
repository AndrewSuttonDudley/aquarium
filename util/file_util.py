import json


def load_json_file(filename) -> dict:
    with open(filename) as json_file:
        config = json.load(json_file)
        print(f'JSON ({filename}) loaded')
        return config
