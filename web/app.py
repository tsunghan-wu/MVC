import flask
import base64
import numpy as np
import cv2
import os

# Initialize the useless part of the base64 encoded image.
init_Base64 = 21

# Our dictionary
label_dict = {0: 'Cat', 1: 'Giraffe', 2: 'Sheep', 3: 'Bat', 4: 'Octopus', 5: 'Camel'}

# Initializing new Flask instance. Find the html template in "templates".
app = flask.Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'upload_images'


# First route : Render the initial drawing template
@app.route('/', methods=['GET'])
def index():
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


@app.route('/draw')
def draw():
    return flask.render_template('draw.html')


# Second route : Use our model to make prediction - render the results page.
@app.route('/predict', methods=['POST'])
def predict():
    if flask.request.method == 'POST':
        final_pred = None
        # Preprocess the image : set the image to 28x28 shape
        # Access the image
        draw = flask.request.form['url']
        # Removing the useless part of the url.
        draw = draw[init_Base64:]
        # Decoding
        draw_decoded = base64.b64decode(draw)
        image = np.asarray(bytearray(draw_decoded), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
        # Resizing and reshaping to keep the ratio.
        resized = cv2.resize(image, (28, 28), interpolation=cv2.INTER_AREA)
        vect = np.asarray(resized, dtype="uint8")
        vect = vect.reshape(1, 1, 28, 28).astype('float32')
        # Launch prediction
        # my_prediction = model.predict(vect)
        # Getting the index of the maximum prediction
        # index = np.argmax(my_prediction[0])
        index = 1
        # Associating the index and its value within the dictionnary
        final_pred = label_dict[index]

        return flask.render_template('results.html', prediction=final_pred)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8998)
