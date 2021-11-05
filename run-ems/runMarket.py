import sys

import requests
import json
import jsonschema

#BASE_URL =  "http://192.168.2.36:9000/api/v1/"
BASE_URL = "https://em.gecad.isep.ipp.pt/api/v1/"
INPUT_FILE = "input.json"
OUTPUT_FILE = "outputMarket.json"
GENERAL_SCHEMA = "resources/generalSchema.json"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def read_file(inputFile):
    f = open(inputFile, "r")
    return f.read()


def write_file(output):
    f = open(OUTPUT_FILE, "w")
    json.dump(output, f, indent=4)
    f.close()


def run_market(input):
    url = BASE_URL + input["run"]
    response = requests.post(url, json=input["input"], headers=HEADERS)
    if response.status_code != 200:
        print(response.text)
        sys.exit(1)
    return response.text


def get_schema(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("The Schema Path does not exist")
        sys.exit(1)
    return response.text


def validate(input):
    try:
        input_json = json.loads(input)
        general_schema_file = json.loads(read_file(GENERAL_SCHEMA))
        jsonschema.validate(instance=input_json, schema=general_schema_file)
        market = input_json["run"]
        market_schema_file = BASE_URL + market + "/schema"
        schema_json = json.loads(get_schema(market_schema_file))
        jsonschema.validate(instance=input_json["input"], schema=schema_json)
        return input_json
    except Exception as err:
        print(err.message)
        sys.exit(1)


if __name__ == "__main__":
    # Run Market
    input = read_file(INPUT_FILE)
    input_json = validate(input)
    result_json = run_market(input_json)
    write_file(json.loads(result_json))
