from flask import Flask, render_template, request, jsonify

from config import *
from imgedit import crop_src_patch, prepare
from mvc import MVC_Cloner


app = Flask(__name__, template_folder='templates')
cloner = MVC_Cloner()


@app.route('/')
def home():
    args = {
        'jpoly_width': JPOLY_WIDTH,
        'jpoly_height': JPOLY_HEIGHT,
        'konva_width': KONVA_WIDTH,
        'konva_height': KONVA_HEIGHT,
    }
    return render_template('example.html', **args)


@app.route('/crop', methods=['POST'])
def crop():
    crop_src_patch(request.get_json())
    return ''


@app.route('/clone', methods=['POST'])
def clone():
    print(request.get_json())
    import numpy as np
    import cv2
    src, tar, bndry, pos = prepare(request.get_json())
    print(src.shape, tar.shape, pos)
    img = src.copy()
    for p in bndry:
        img = cv2.circle(img, p, radius=1, color=(0, 0, 255))
    cv2.imwrite('tr.png', img)
    output = cloner.process(src, tar, np.array([src.shape[1]//2, src.shape[0]//2]), pos, 
        np.int32(bndry))

    cv2.imwrite('test.png', output)

    return ''
