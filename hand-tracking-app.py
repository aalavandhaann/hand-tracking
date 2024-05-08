# Based on the tutorial https://auth0.com/blog/developing-restful-apis-with-python-and-flask/
import base64
import pathlib

import cv2
import numpy as np
from engineio.payload import Payload
from flask import (Flask, Response, render_template, request, send_file,
                   send_from_directory, url_for)
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from handtracker.handtracker import HandTracker

Payload.max_decode_packets = 50

BASE_PATH: pathlib.Path = pathlib.Path(__file__).parent
ALLOWED_EXTENSIONS = {'jpg', 'png'}



camera = None
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config['IMAGES'] = BASE_PATH.joinpath('images')

socketio = SocketIO(app, async_mode="eventlet")

hand_tracker = HandTracker()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def base64_to_image(base64_string):
    """
    The base64_to_image function accepts a base64 encoded string and returns an image.
    The function extracts the base64 binary data from the input string, decodes it, converts 
    the bytes to numpy array, and then decodes the numpy array as an image using OpenCV.
    
    :param base64_string: Pass the base64 encoded image string to the function
    :return: An image
    """
    base64_data = base64_string.split(",")[1]
    image_bytes = base64.b64decode(base64_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


@socketio.on("connect")
def test_connect():
    """
    The test_connect function is used to test the connection between the client and server.
    It sends a message to the client letting it know that it has successfully connected.
    
    :return: A 'connected' string
    """
    print("Connected")
    emit("my response", {"data": "Connected"})




@socketio.on("image")
def receive_image(image):
    """
    The receive_image function takes in an image from the webcam, converts it to grayscale, and then emits
    the processed image back to the client.


    :param image: Pass the image data to the receive_image function
    :return: The image that was received from the client
    """
    
    
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    
    # Decode the base64-encoded image data
    image = base64_to_image(image)
    
    frame_resized = hand_tracker.findHands(image)
    landmark_list = hand_tracker.findHandLandmarks(frame_resized)
        
     
    ret, frame_encoded = cv2.imencode('.jpg', frame_resized, encode_param)
    processed_img_data = base64.b64encode(frame_encoded).decode()    
    b64_src = "data:image/jpg;base64,"
    processed_img_data = b64_src + processed_img_data
    
    
    emit("processed_image", processed_img_data)


@app.route("/", methods=['GET', 'POST'])
def index():
    print('requesting ', request.files)
    return render_template("index-live.html"), 200


@app.route("/js/<path:filename>", methods=['GET', 'POST'])
def jsfile(filename):
    print('requesting js file : ', filename)
    return send_file(f'templates/static/{filename}'), 200

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    socketio.run(app, debug=True, port=5000, host='0.0.0.0', certfile="server.crt", keyfile="server.key")