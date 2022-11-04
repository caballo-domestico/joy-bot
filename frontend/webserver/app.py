from crypt import methods
import email
from flask import Flask, render_template, request, flash, send_file, redirect, make_response
import os
from werkzeug.utils import secure_filename
from random import randint
import botocore
import boto3
from botocore.config import Config
from rpcCalls import RegistrationClient
from dao import PrescriptionsDao, PrescriptionBean
from tempfile import TemporaryFile
from urllib.parse import quote_plus
from flask_bootstrap import Bootstrap5
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.urandom(24).hex()
ALLOWED_EXTENSIONS = {'pdf', "png", "jpg", "jpeg"}

@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/signin', methods=('GET', 'POST'))
def signin():
    auth = 'auth.html'
    if request.method == 'POST':
        email = request.form.get("umail")
        password = request.form.get("upass")
        user_type = request.form.get("utype")
        phone_num = request.form.get("uphone")
        resp = user_cookie(email, auth)
        rpc_obj = RegistrationClient()
        rpc_obj.get_user(email=email, password=password, user_type=user_type, phone_num=phone_num, confirmed=False)
        #sms_sender(phone_num)
        return resp
    return render_template('signin.html')

@app.route('/auth', methods=('GET', 'POST'))
def confirmation():
    if request.method == 'POST':
        name = request.cookies.get('usermail')
        logging.info("HERE")
        logging.info(name)
        return render_template('index.html')
    return render_template('auth.html')

def user_cookie(email, page):
    resp = make_response(render_template(page))
    resp.set_cookie('usermail', email)
    return resp 


def sms_sender(phone_num):
    sns = boto3.resource("sns")
    pin = randint(100000, 999999)
    message = "This is your account verification pin:{}".format(pin) 
    sns.meta.client.publish(PhoneNumber=phone_num, Message=message)
    try:
        sns.meta.client.publish(PhoneNumber=phone_num, Message=message)
        logging.info("Published message to %s.", phone_num)
    except botocore.exceptions.ClientError:
        logging.exception("Couldn't publish message to %s.", phone_num)
        raise
    else:
        return pin


@app.route('/upload-prescription', methods=('GET', 'POST'))
def upload_prescription():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'prescription' not in request.files:
            flash('No prescription selected', "danger")
        file = request.files['prescription']
        if file.filename == '':
            flash('No selected file', "danger")
        if file and not allowed_file(file.filename):
            flash(f'file types allowed: {ALLOWED_EXTENSIONS}', "danger")
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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
