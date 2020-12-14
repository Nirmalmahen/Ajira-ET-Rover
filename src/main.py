import json, sys

from flask import Response,request
from flask_restful import reqparse

from . import create_app
from .models.Rover import Rover
from .models.Inventory import InventoryItem, addItem

app = create_app()
rover=Rover()
env = rover.Environment
inventory=rover.Inventory
inventoryItem=InventoryItem()

env_args = reqparse.RequestParser()
env_args.add_argument("temperature", type=int)
env_args.add_argument("humidity", type=int)
env_args.add_argument("solar-flare", type=bool)
env_args.add_argument("storm", type=bool)
env_args.add_argument("area-map", type=[[]])

@app.route('/api/environment/configure', methods=['POST'])
def configEnv():
    data = env_args.parse_args()
    rover.Environment.temperature = data['temperature']
    rover.Environment.humidity = data['humidity']
    rover.Environment.flare = data['solar-flare']
    rover.Environment.storm = data['storm']
    rover.Environment.terrain = data['area-map']
    rover.Environment.area_max_row = len(rover.Environment.terrain)
    rover.Environment.area_max_col = len(rover.Environment.terrain[0])
    return Response(response=json.dumps(""),
                    status=200,
                    mimetype="application/json")

@app.route('/api/environment', methods=['PATCH'])
def updateEnv():
    if not request.is_json:
        return Response(response=json.dumps(errorResponse(400, "Rover accepts only JSON request")),
                        status=400,
                        mimetype="application/json")

    data = env_args.parse_args()
    if data['temperature']:
        rover.Environment.temperature = data['temperature']
    if data['humidity']:
        rover.Environment.humidity = data['humidity']
    if data['solar-flare']:
        rover.Environment.flare = data['solar-flare']
        if rover.Environment.flare == True:
            rover.battery = 11
    if data['storm']:
        rover.Environment.storm = data['storm']
        if rover.Environment.storm == True:
            rover.state = "immobile"
            useSheild()
        else:
            rover.state = "mobile"
    return Response(response=json.dumps(""),
                    status=200,
                    mimetype="application/json")

def useSheild():
    if not rover.Inventory.inventoryItemsSampleList[1]:
        sys.exit()
    else:
        rover.Inventory.inventoryItemsSampleList[1]-=1

@app.route('/api/rover/configure', methods=['POST'])
def configRover():
    data = request.get_json()
    rover.position["row"] = data['deploy-point']['row']
    rover.position["column"] = data['deploy-point']['column']
    rover.battery = data['initial-battery']
    inventoryItemsList=data['inventory']
    invItem=InventoryItem()
    for item in inventoryItemsList:
        invItem.sampleName=item['type']
        invItem.samplePriority=item['priority']
        invItem.sampleSize=item['quantity']
        addItem(invItem,rover.Inventory)
    return Response(response=json.dumps(""),
                    status=200,
                    mimetype="application/json")

@app.route('/api/rover/move', methods=['POST'])
def moveRover():
    outOfBoundsErrResponse=Response(response=json.dumps(errorResponse(428, "Can move only within mapped area")),
             status=428,
             mimetype="application/json")
    if not request.is_json:
        return Response(response=json.dumps(errorResponse(400, "Rover accepts only JSON request")),
                        status=400,
                        mimetype="application/json")
    if rover.state is "immobile":
        return Response(response=json.dumps(errorResponse(428, "Cannot move during a storm")),
                        status=428,
                        mimetype="application/json")
    data = request.get_json()
    direction = data['direction']
    batteryCheck()
    prevXPos=rover.position['row']
    prevYPos=rover.position['column']
    if direction is "up" :
        xPosistion=rover.position["row"]-1
        if xPosistion<0:
            return outOfBoundsErrResponse
        else:
            rover.position["row"] -= 1
    if direction is "down" :
        xPosistion=rover.position["row"]+1
        if xPosistion>rover.Environment.area_max_row-1:
            return outOfBoundsErrResponse
        else:
            rover.position["row"] += 1
    if direction is "left" :
        yPosistion=rover.position["column"]-1
        if yPosistion<0:
            return outOfBoundsErrResponse
        else:
            rover.position["column"] -= 1
    if direction is "right" :
        yPosistion=rover.position["column"]-1
        if yPosistion>rover.Environment.area_max_col-1:
            return outOfBoundsErrResponse
        else:
            rover.position["column"] -= 1
    rover.battery-=1
    currentTerrain=rover.Environment.terrain[rover.position["row"]][rover.position["column"]]
    if rover.Environment.terrain[prevXPos][prevYPos] is not currentTerrain:
        if currentTerrain is "water":
            collectSample("water")
        elif currentTerrain is "rock":
            collectSample("rock")

    return Response(response=json.dumps(""),
                    status=200,
                    mimetype="application/json")

def batteryCheck():
    if(rover.battery<2):
        rover.battery=10
    else:
        pass


def collectSample(sampleType):
    if(sampleType is "water"):
        invItem = InventoryItem()
        invItem.name="water-sample"
        invItem.priority=2
        invItem.size=2
        addItem(invItem,rover.Inventory)
    elif(sampleType is "rock"):
        invItem = InventoryItem()
        invItem.name="rock-sample"
        invItem.priority=3
        invItem.size=3
        addItem(invItem,rover.Inventory)


@app.route('/api/rover/status', methods=['GET'])
def roverStatus():
    roverRespJson,enviRespJson,respJson=any()
    roverRespJson["location"]=rover.position
    roverRespJson["battery"]=rover.battery
    inventoryItemsList=[]
    if rover.Inventory.items["1"]:
        invItem={
                "type":"storm-sheild",
                "quantity":rover.Inventory.items["1"],
                "priority":1
            }
        inventoryItemsList.append(invItem)
    elif rover.Inventory.items["2"]:
        invItem = {
            "type": "water-sample",
            "quantity": rover.Inventory.items["2"],
            "priority": 2
        }
        inventoryItemsList.append(invItem)
    elif rover.Inventory.items["3"]:
        invItem = {
            "type": "rock-sample",
            "quantity": rover.Inventory.items["3"],
            "priority": 3
        }
        inventoryItemsList.append(invItem)
    roverRespJson["inventory"]=inventoryItemsList
    enviRespJson["temperature"]=rover.Environment.temperature
    enviRespJson["humidity"] = rover.Environment.humidity
    enviRespJson["solar-flare"] = rover.Environment.flare
    enviRespJson["storm"] = rover.Environment.storm
    enviRespJson["terrain"] = rover.Environment.terrain[rover.position["row"]][rover.posistion["column"]]
    respJson["rover"]=roverRespJson
    respJson["environment"] = enviRespJson
    return Response(response=json.dumps(respJson),
                    status=200,
                    mimetype="application/json")

def errorResponse(statusCode, message):
    resultResponse = {
        "code": statusCode,
        "message": message
    }
    return resultResponse
