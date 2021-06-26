import os
import json
import flask


# Initializing new Flask instance. Find the html template in "templates".
app = flask.Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'upload_images'


# First route : Render the initial drawing template
@app.route('/', methods=['GET'])
def index():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    srcfname = os.path.join(app.config['UPLOAD_FOLDER'], "src.png")
    dstfname = os.path.join(app.config['UPLOAD_FOLDER'], "dst.png")
    if os.path.exists(srcfname):
        os.remove(srcfname)
    if os.path.exists(dstfname):
        os.remove(dstfname)
    return flask.render_template('index.html')


@app.route('/upload_src', methods=['POST'])
def upload_src():
    print(flask.request, flush=True)
    file = flask.request.files['src_img']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], "src.png")
    file.save(filename)
    return flask.make_response("Success", 201)


@app.route('/upload_dst', methods=['POST'])
def upload_dst():
    print(flask.request, flush=True)
    file = flask.request.files['dst_img']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], "dst.png")
    file.save(filename)
    return flask.make_response("Success", 201)


@app.route('/checkfile', methods=['GET'])
def checkfile():
    print("checkfile", flush=True)
    srcfname = os.path.join(app.config['UPLOAD_FOLDER'], "src.png")
    dstfname = os.path.join(app.config['UPLOAD_FOLDER'], "dst.png")
    if os.path.exists(srcfname) and os.path.exists(dstfname):
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8998)
