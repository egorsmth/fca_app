import os
from flask import Flask, render_template, url_for, json, jsonify, request
from flask_cors import CORS
import base64

import core

OUT_FILE_NAME = "conc.png"

def getFromJson(filename):
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, filename+".json")
    data = json.load(open(json_url))
    return data

def encodedFile(filename):
  SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
  img_url = os.path.join(SITE_ROOT, filename)
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
    core.draw(b, OUT_FILE_NAME)
    resp = dict({
      'latticeImg': encodedFile(OUT_FILE_NAME),
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
    (newCtx, L) = core.addAttr(a, b, attrM, attrMI)
    core.draw(L, OUT_FILE_NAME)
    resp = dict({
      'latticeImg': encodedFile(OUT_FILE_NAME),
      'lattice': b.toJson(),
      'concept': a.toJson()
    })
    return jsonify(resp)

