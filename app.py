import os
import random
import cv2
import flask

from imgedit import crop_src_patch, prepare
from mvc import MVC_ClonerFast


# Initializing new Flask instance. Find the html template in "templates".
app = flask.Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'static/data'

cloner = MVC_ClonerFast()


# First route : Render the initial drawing template
@app.route('/', methods=['GET'])
def index():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    srcfname = os.path.join(app.config['UPLOAD_FOLDER'], "src.png")
    dstfname = os.path.join(app.config['UPLOAD_FOLDER'], "tar.png")
    resultfname = os.path.join(app.config['UPLOAD_FOLDER'], "result.png")
    if os.path.exists(srcfname):
        os.remove(srcfname)
    if os.path.exists(dstfname):
        os.remove(dstfname)
    if os.path.exists(resultfname):
        os.remove(resultfname)
    return flask.render_template('index.html')


@app.route('/upload_src', methods=['POST'])
def upload_src():
    print(flask.request, flush=True)
    file = flask.request.files['src_img']
    fileID = f'{random.randint(0, 99):02d}'
    filename = os.path.join(app.config['UPLOAD_FOLDER'], f"src{fileID}.png")
    file.save(filename)
    return fileID


@app.route('/upload_dst', methods=['POST'])
def upload_dst():
    print(flask.request, flush=True)
    file = flask.request.files['dst_img']
    fileID = f'{random.randint(0, 99):02d}'
    filename = os.path.join(app.config['UPLOAD_FOLDER'], f"tar{fileID}.png")
    file.save(filename)

    return fileID


def delete(dtype, fileID):
    name = dtype + fileID + '.png'
    path = os.path.join(app.config['UPLOAD_FOLDER'], name)
    if os.path.exists(path):
        os.remove(path)
        print("Removed", name)
    else:
        print(name, "is not existed")


@app.route('/del_src', methods=['DELETE'])
def del_src():
    delete('src', flask.request.data.decode())
    return ''


@app.route('/del_dst', methods=['DELETE'])
def del_dst():
    delete('tar', flask.request.data.decode())
    return ''


# @app.route('/checkfile', methods=['GET'])
# def checkfile():
#     print("checkfile", flush=True)
#     srcfname = os.path.join(app.config['UPLOAD_FOLDER'], "src.png")
#     dstfname = os.path.join(app.config['UPLOAD_FOLDER'], "tar.png")
#     if os.path.exists(srcfname) and os.path.exists(dstfname):
#         return flask.jsonify({'success': True})
#     else:
#         return flask.jsonify({'success': False})


@app.route('/crop', methods=['POST'])
def crop():
    info = flask.request.get_json()
    crop_src_patch(info['srcID'], info['perimeter'], info['width'], info['height'])
    return ''


@app.route('/clone', methods=['POST'])
def clone():
    info = flask.request.get_json()
    src, tar, bndry, pos = prepare(info, src_name=f"src{info['srcID']}.png",
                                   patch_name=f"patch{info['srcID']}.png", tar_name=f"tar{info['tarID']}.png")
    if info['method'] == 'vanilla':
        output = cloner.process(src, tar, [src.shape[1]//2, src.shape[0]//2],
                                pos, bndry)
    elif info['method'] == 'fast':
        output = cloner.adaptive_process(src, tar, [src.shape[1]//2, src.shape[0]//2],
                                         pos, bndry)
    fileID = random.randint(0, 99)
    resultfname = os.path.join(app.config['UPLOAD_FOLDER'], f"result{fileID:02d}.png")
    cv2.imwrite(resultfname, output)

    return f'{fileID:02d}'


# @app.route('/checkresult', methods=['GET'])
# def checkresult():
#     print("checkresult", flush=True)
#     resultfname = os.path.join(app.config['UPLOAD_FOLDER'], "result.png")
#     if os.path.exists(resultfname):
#         return flask.jsonify({'success': True})
#     else:
#         return flask.jsonify({'success': False})

@app.route('/clear_result', methods=['POST'])
def clear_result():
    data = flask.request.get_json()
    delete('patch', data['srcID'])
    delete('result', data['resID'])
    return ''


@app.route('/clear', methods=['POST'])
def clear():
    data = flask.request.get_json()
    for dtype, fileID in zip(['src', 'patch', 'tar', 'result'],
                             [data['srcID'], data['srcID'], data['tarID'], data['resID']]):
        delete(dtype, fileID)
    return ''


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8998)
