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
WITHOUT_MASK = "Không đeo khẩu trang"
WITH_MASK = "Đeo khẩu trang"


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


@app.route('/send', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']

    URL = "http://127.0.0.1:30701"
    param = request.files
    response = requests.post(URL, files=param)

    if file and allowed_file(file.filename):
        if response.status_code != 500 and response.ok:
            my_json = response.content.decode('utf8').replace("'", '"')
            data = json.loads(my_json)
            s = json.dumps(data, indent=4, sort_keys=True)
            listResponse = json.loads(s)
            lable = listResponse[0][0]
            result = ""
            if lable == "without_mask":
                result = WITHOUT_MASK
            if lable == "with_mask":
                result = WITH_MASK
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Image successfully uploaded and displayed below')
            return render_template('./index.html', filename=filename, result=result)
        return "<h2>Can not regnization</h2>"
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    else:
        flash('Allowed image type are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/webcamera')
def webcamera():
    return render_template('./camera.html')

@app.route("/modal")
def modal():
    return render_template('modal.html')

if __name__ == "__main__":
    app.run()
