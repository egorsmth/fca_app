import os
from flask import Flask, render_template, url_for, json, jsonify, request
from flask_cors import CORS
import base64
from datetime import datetime

import core
import draw
import addAttribute
import nextNeighbour

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
    start = datetime.now()
    b = nextNeighbour.nextNeighbours(a)
    end = datetime.now()

    draw_start = datetime.now()
    draw.draw(b, OUT_FILE_NAME)
    draw_end = datetime.now()

    resp = dict({
      'latticeImg': encodedFile(OUT_FILE_NAME),
      'lattice': b.toJson(),
      'concept': a.toJson(),
      'constructTime': (end - start).total_seconds(),
      'drawTime': (draw_end - draw_start).total_seconds(),
      'json': json.dumps(dict(G = a.G, M = a.M, I = a.I)) 
    })
    return jsonify(resp)

from json import JSONEncoder
class MyEncoder(JSONEncoder):
    def __init__(self, G, M, I):
        self.G = G
        self.I = I
        self.M = M
    def default(self, o):
        return o.__dict__    


@app.route('/addattr',  methods=['POST'])
def add_attribute():
  try:
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
    start = datetime.now()
    (newCtx, L) = addAttribute.addAttr(a, b, attrM, attrMI)
    end = datetime.now()

    draw_start = datetime.now()
    draw.draw(L, OUT_FILE_NAME)
    draw_end = datetime.now()

    resp = dict({
      'latticeImg': encodedFile(OUT_FILE_NAME),
      'lattice': b.toJson(),
      'concept': a.toJson(),
      'drawTime': (draw_end - draw_start).total_seconds(),
      'addTime': (end - start).total_seconds(),
      'json': json.dumps(dict(G = newCtx.G, M = newCtx.M, I = newCtx.I)) 
    })
    return jsonify(resp)
  except:
    return "Wrong input", 400

from flask import abort
from werkzeug.exceptions import BadRequest

def check_import_concept(concept):
    glen = len(concept["G"])
    mlen = len(concept["M"])
    if (mlen == 0 or glen == 0):
      raise Exception("M or G len is 0")
    if (len(concept["I"]) is not glen):
      raise Exception("I != G len")
    if not all( list(map(lambda s : isinstance(s, str), concept["G"])) ):
      raise Exception("G must be list of strings")
    if not all( list(map(lambda s : isinstance(s, str), concept["M"])) ):
      raise Exception("N nust be list of strings")
    for i in concept["I"]:
      if not (len(i) is mlen and all( list(map(lambda x: x == 0 or x == 1, i)))):
        raise Exception("I must consist of 0 or 1 and length myst be equal to attributs")
    
@app.route('/upload', methods=['POST'])
def fileUpload():
    file = request.files['file'] 
    destination="/".join([os.path.realpath(os.path.dirname(__file__)), "concept2.json"])
    file.save(destination)
    ###
    concept = getFromJson("concept2")
    try:
      check_import_concept(concept)
    except Exception as e:
      return "{0}".format(e), 400

    a = core.Context(concept["G"],
        concept["M"],
        concept["I"])
    start = datetime.now()
    b = nextNeighbour.nextNeighbours(a)
    end = datetime.now()

    draw_start = datetime.now()
    draw.draw(b, OUT_FILE_NAME)
    draw_end = datetime.now()

    resp = dict({
      'latticeImg': encodedFile(OUT_FILE_NAME),
      'lattice': b.toJson(),
      'concept': a.toJson(),
      'constructTime': (end - start).total_seconds(),
      'drawTime': (draw_end - draw_start).total_seconds(),
      'json': json.dumps(dict(G = a.G, M = a.M, I = a.I)) 
    })
    return jsonify(resp)

from flask import send_file, send_from_directory
from flask import Response
    
@app.route('/download', methods=['POST'])
def download():
    data = request.json['json']
    destination="/".join([os.path.realpath(os.path.dirname(__file__)), "out.json"])
    f = open(destination, 'w+')
    f.write(data)
    return send_file(f, attachment_filename=destination)

