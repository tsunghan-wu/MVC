from flask import Flask, render_template, request, jsonify

from imgedit import crop_src_patch, prepare
from mvc import MVC_Cloner


app = Flask(__name__, template_folder='templates')
cloner = MVC_Cloner()


@app.route('/')
def home():
    return render_template('example.html')


@app.route('/crop', methods=['POST'])
def crop():
    info = request.get_json()
    crop_src_patch(info['perimeter'], info['width'], info['height'])
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
        img = cv2.circle(img, p, radius=2, color=(0, 0, 255))

    cv2.imwrite('tr.png', img)
    tar = cv2.circle(tar, pos, radius=2, color=(255, 0, 0))
    # tar = cv2.circle(tar, pos+center, radius=2, color=(255, 0, 0))
    cv2.imwrite('tart.png', tar)
    output = cloner.process(src, tar, np.array([src.shape[1]//2, src.shape[0]//2]), pos, 
        np.int32(bndry))

    cv2.imwrite('test.png', output)

    return ''
