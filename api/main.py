import os
from flask import Flask, render_template, url_for, json, jsonify, request
from flask_cors import CORS
import base64

import core

def getFromJson(filename):
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, filename+".json")
    data = json.load(open(json_url))
    return data

def encodedFile(filename):
  SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
  img_url = os.path.join(SITE_ROOT, filename)
  print(img_url)
  data = open(img_url, "rb").read()
  encoded = str(base64.b64encode(data))
  return encoded

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    concept = getFromJson("concept")
    a = core.Context(concept["G"],
        concept["M"],
        concept["I"])
    b = core.nextNeighbours(a)
    # print("MAIN")
    # print(a)
    # print(b.C)
    # print(list(map(lambda x: x.__hash__(), b.C)))
    # print(b.E)
    # print("+++++++++++++++++++++++++++++++++++++")
    outFileName = "test1.png"
    core.draw(b, outFileName)
    resp = dict({
      'latticeImg': encodedFile(outFileName),
      'lattice': b.toJson(),
      'concept': a.toJson()
    })
    return jsonify(resp)

@app.route('/addattr',  methods=['POST'])
def add_attribute():
    current_concept = request.json["old_concept"]
    current_lattice = request.json["old_lattice"]
    attrM = request.json["attrM"]
    attrMI = request.json["attrMI"]

    a = core.Context(current_concept["G"],
        current_concept["M"],
        current_concept["I"])
    b = core.Lattice(
      list(map(lambda x: core.Node(set(x["G"]), set(x["M"])), current_lattice["C"])), 
      set(map(lambda x: (int(x[0]), int(x[1])), current_lattice["E"]))
    )
    # print("ADD ATTR")
    # print(a)
    # print(b.C)
    # print(list(map(lambda x: x.__hash__(), b.C)))
    # print(b.E)
    # print("+++++++++++++++++++++++++++++++++++++")
    print(attrM, attrMI)
    print("JOJ", [1,0,0,0,1,0, 0])
    print(attrM=="JOJ", attrMI==[1,0,0,0,1,0, 0])
    (newCtx, L) = core.addAttr(a, b, attrM, attrMI)
    outFileName = "test2.png"
    core.draw(L, outFileName)
    resp = dict({
      'latticeImg': encodedFile(outFileName),
      'lattice': b.toJson(),
      'concept': a.toJson()
    })
    return jsonify(resp)

