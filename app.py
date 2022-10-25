from fileinput import filename
from sre_constants import SUCCESS
from flask import Flask, flash, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
import os
import cv2
import urllib.request
import requests
import json


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.secret_key = "cairocoders-ednalan"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_frames():
    camera = cv2.VideoCapture("some_m3u8_link")
    while True:
        # read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def home():
    return render_template('./index.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Image successfully uploaded and displayed below')
        URL = "http://127.0.0.1:30701"
        response = requests.post(URL, files=request.files)
        print(type(response.content))
        if response != None and response.content != None:
            my_json = response.content.decode('utf8').replace("'", '"')
            print(my_json)
            print('- ' * 20)

            data = json.loads(my_json)
            s = json.dumps(data, indent=4, sort_keys=True)
            print(s)
            return render_template('./index.html', filename=filename)
    else:
        flash('Allowed image type are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/webcamera')
def webcamera():
    return render_template('./camera.html')


if __name__ == "__main__":
    app.run()
