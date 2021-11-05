import json
import jsonschema
import sys
import copy
import requests


INPUT_FILE_MARKET = "outputMarket.json"
INPUT_FILE_PBUS = "playersBuses.json"
INPUT_FILE_PFS = "inputPFS.json"
PBUS_SCHEMA = "resources/pbus_schema.json"
PFS_SCHEMA = "resources/pfs_schema.json"
OUTPUT_FILE = "outputPowerFlow.json"
URL = "https://pf.gecad.isep.ipp.pt/api/v1/networks/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def read_file(inputFile):
    f = open(inputFile, "r", encoding="utf8")
    return f.read()


def write_file(output):
    f = open(OUTPUT_FILE, "w")
    json.dump(output, f, indent=4)
    f.close()


def validate(file, schema):
    try:
        file_json = json.loads(file)
        schema = json.loads(read_file(schema))
        jsonschema.validate(instance= file_json, schema= schema)
        return file_json
    except Exception as err:
        print(str(err))
        sys.exit(1)

def create_input_pfs(input_pfs, output_market, player_buses, i, id):
    if "loads" not in input_pfs["network"]["elements"]:
        input_pfs["network"]["elements"]["loads"]=[]
    for index, player in enumerate(output_market["session"]["playersResult"]):
        id+=1
        bus = -1
        for element in player_buses["playersBuses"]:
            if element["player"] == player["playerId"]:
                bus = element["bus"]
        if bus == -1:
            print("Player "+ player["playerId"] +"not found !")
            sys.exit(1)
        active_power = output_market["session"]["playersResult"][index]["playerPeriodsResult"][i]["satisfied"] if "satisfied" in output_market["session"]["playersResult"][index]["playerPeriodsResult"][i] else 0 
        input_pfs["network"]["elements"]["loads"].append(
            {
                "id": id,
                "name": "load " + str(id),
                "bus": bus,
                "activePower": active_power
            }
        )
    return input_pfs
        

def run_power_flow(input):
    response = requests.post(URL, json= input, headers = HEADERS)
    return response


def build_result(results, response, i):
    if response.status_code != 200:
        results["results"].append(
            {
                "period": i+1,
                "error": response.json()
            }
        )
    else:
        results["results"].append(
            {
                "period": i+1,
                "result": response.json()
            }
        )


if __name__ == "__main__":
    output_market = json.loads(read_file(INPUT_FILE_MARKET))
    players_buses = validate(read_file(INPUT_FILE_PBUS),PBUS_SCHEMA)
    input_pfs = validate(read_file(INPUT_FILE_PFS), PFS_SCHEMA)
    input_pfs2 = copy.deepcopy(input_pfs)
    if "loads" in input_pfs2["network"]["elements"]:
        loads = input_pfs2["network"]["elements"]["loads"]
        input_pfs2["network"]["elements"].clear()
        input_pfs2["network"]["elements"]["loads"] = loads
    else:
        input_pfs2["network"]["elements"].clear()
    max_p = max(result["period"] for result in output_market["session"]["periods"])
    max_id=-1
    for skip in input_pfs["network"]["elements"]:
        temp = max(ids["id"] for ids in input_pfs["network"]["elements"][skip])
        max_id = temp if temp > max_id else max_id
    results= {"results":[]}
    for i in range(max_p):
        if i > 0:
            input = create_input_pfs(copy.deepcopy(input_pfs2), output_market, players_buses,i, max_id)
        else:
            input = create_input_pfs(copy.deepcopy(input_pfs), output_market, players_buses,i, max_id)
        response = run_power_flow(input)
        build_result(results, response,i)
    write_file(results)
