import cv2
import tempfile
import os
import uuid
from flask import Flask,jsonify,render_template,send_file,redirect,request
from werkzeug.utils import secure_filename
from OBR import SegmentationEngine,BrailleClassifier,BrailleImage


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
tempdir = tempfile.TemporaryDirectory()

app = Flask("Optical Braille Recognition Demo")
app.config['UPLOAD_FOLDER'] = tempdir.name

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/favicon.ico')
def fav():
    return send_file('favicon.ico', mimetype='image/ico')

@app.route('/coverimage')
def cover_image():
    return send_file('samples/sample1.png', mimetype='image/png')

@app.route('/procimage/<string:img_id>')
def proc_image(img_id):
    global tempdir
    print(img_id)
    image = '{}/{}-proc.png'.format(tempdir.name, secure_filename(img_id))
    if os.path.exists(image) and os.path.isfile(image):
        return send_file(image, mimetype='image/png')
    return redirect('/coverimage')

@app.route('/digest', methods=['POST'])
def upload():
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error" : True, "message" : "file not in request"})
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": True, "message" : "empty filename"})
    if file and allowed_file(file.filename):
        filename = ''.join(str(uuid.uuid4()).split('-'))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        global tempdir
        
        image_path = '{}/{}'.format(tempdir.name,filename)
        classifier = BrailleClassifier()
        img = BrailleImage(image_path)
        for letter in SegmentationEngine(image=img):
            letter.mark()
            classifier.push(letter)
        cv2.imwrite('{}/{}-proc.png'.format(tempdir.name,filename), img.get_final_image())
        os.unlink(image_path)

        r = {
                "error": False,
                "message": "Processed and Digested successfully",
                "img_id" : filename,
                "digest" : classifier.digest()
        }
        return jsonify(r)

if __name__ == "__main__":
    app.run()
    tempdir.cleanup()
