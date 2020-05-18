import threading
import cv2
import tempfile
import os
from flask import Flask,render_template,send_file,redirect,request
from werkzeug.utils import secure_filename
from OBR import SegmentationEngine,BrailleClassifier,BrailleImage

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
tempdir = tempfile.TemporaryDirectory()
lock = threading.Lock()
image_path = 'samples/sample1.png'
classifier = BrailleClassifier()

app = Flask("Optical Braille Recognition Demo")
app.config['UPLOAD_FOLDER'] = tempdir.name

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/current_image')
def current_image():
    global lock
    lock.acquire()
    global image_path
    image = image_path
    lock.release()
    return send_file(image, mimetype='image/png')

@app.route('/processed_image')
def proc_image():
    global tempdir
    return send_file('{}/proc.png'.format(tempdir.name), mimetype='image/png')

@app.route('/digest')
def digest():
    global lock
    lock.acquire()
    global image_path
    global classifier
    global tempdir
    img = BrailleImage(image_path)
    classifier.clear()
    for letter in SegmentationEngine(image=img):
        letter.mark()
        classifier.push(letter)
    cv2.imwrite('{}/proc.png'.format(tempdir.name), img.get_final_image())
    lock.release()
    return classifier.digest()

@app.route('/upload', methods=['POST'])
def upload():
    # check if the post request has the file part
    if 'file' not in request.files:
        return redirect('/')
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return redirect('/')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded'))
        global lock
        lock.acquire()
        global image_path
        global tempdir
        image_path = '{}/uploaded'.format(tempdir.name)
        lock.release()
        return redirect('/')

if __name__ == "__main__":
    app.run()
    tempdir.cleanup()
