from crypt import methods
import email
from flask import Flask, render_template, request, flash, send_file, redirect
import os
from werkzeug.utils import secure_filename
import boto3
from botocore.config import Config
from webserver.dao import PrescriptionsDao, PrescriptionBean, RegistrationBean, RegistrationDao
from tempfile import TemporaryFile
from urllib.parse import quote_plus
from flask_bootstrap import Bootstrap5
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.urandom(24).hex()
ALLOWED_EXTENSIONS = {'txt', 'pdf', "png", "jpg", "jpeg"}

@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/signin', methods=('GET', 'POST'))
def signin():
    if request.method == 'POST':
        email = request.form.get("umail")
        password = request.form.get("upass")
        user_type = request.form.get("utype")
        registrationDao = RegistrationDao()
        registrationDao.registerUser(registrationBean=RegistrationBean(email=email, password=password, user_type=user_type))
    return render_template('signin.html')

@app.route('/upload-prescription', methods=('GET', 'POST'))
def upload_prescription():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'prescription' not in request.files:
            flash('No prescription selected', "danger")
        file = request.files['prescription']
        if file.filename == '':
            flash('No selected file', "danger")
        if file and allowed_file(file.filename):
            
            # uploads prescription and its metadata to db
            filename = secure_filename(file.filename).replace(" ", "_")        
            username=quote_plus("test")
            dao = PrescriptionsDao()
            bean = PrescriptionBean(username=username, file=file, fileName=filename)
            dao.storePrescription(prescriptionBean=bean)

            return redirect(f"/list-prescriptions?username={username}")
    return render_template('upload-prescription.html')

@app.route('/list-prescriptions', methods=['GET'])
def list_prescriptions():
    username = request.args.get('username', type=str)
    dao = PrescriptionsDao()
    names = dao.loadAllUserPrescriptionsNames(prescriptionBean=PrescriptionBean(username=username))
    return render_template('list-prescriptions.html', names=names, username=username)

@app.route('/get-prescription', methods=['GET'])
def get_prescription():
    dao = PrescriptionsDao()
    fileName = request.args.get('fileName', type=str)
    username = request.args.get('username', type=str)
    buf = TemporaryFile(mode="w+b")
    prescriptionBean = PrescriptionBean(username=username, file=buf, fileName=fileName)
    dao.loadPrescription(prescriptionBean=prescriptionBean)
    buf.seek(0)
    response = send_file(buf, attachment_filename=fileName, as_attachment=True)
    return response

# TODO: remove testing endopint when not needed anymore
#@app.route('/test-publisher', methods=['GET'])
#def test_publisher():
#    PUBLISHER = Publisher()
#    username = "test"
#    filename = "test.txt"
#    metadata=PUBLISHER.send(Topic.PRESCRIPTION_UPLOADED.value, value={"username" : username, "filename" : filename}).get(timeout=30)
#    return "ok"

if __name__ == '__main__':
    app.run(debug=True)
