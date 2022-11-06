from crypt import methods
import email
from flask import Flask, render_template, request, flash, send_file, redirect, make_response
import os
from werkzeug.utils import secure_filename
from random import randint
import botocore
import boto3
from botocore.config import Config
from rpcCalls import RegistrationClient, PrescribedDrugsDao
from dao import PrescriptionsDao, PrescriptionBean
from tempfile import TemporaryFile
from urllib.parse import quote_plus
from flask_bootstrap import Bootstrap5
import logging
import argparse
import pub

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.urandom(24).hex()
ALLOWED_EXTENSIONS = {'pdf', "png", "jpg", "jpeg"}

@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('loginuser.html')

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
        cookies = {
            'userphone':phone_num, 
            'count':'1'
        }
        resp = user_cookie(dict=cookies, page=auth)
        rpc_obj = RegistrationClient()
        rpc_obj.get_user(email=email, password=password, user_type=user_type, phone_num=phone_num, confirmed=False)
        sms_sender(phone_num)
        return resp
    return render_template('signin.html')

@app.route('/auth', methods=('GET', 'POST'))
def confirmation():
    rpc_obj = RegistrationClient()
    logging.info("TRY %s.", str(request.cookies.get('count')))
    if request.method == 'POST':
        op = 'get'
        pin = request.form.get("upin")
        phone_num = request.cookies.get('userphone')
        response = rpc_obj.manage_pin(phone=phone_num, db_op=op, real_user=False)
        db_pin = response.pin

        if(request.cookies.get('count')>='3'):
            op="rm"
            rpc_obj.manage_pin(phone=phone_num, db_op=op, real_user=False)
            return render_template('error.html')

        elif(str(pin) == str(db_pin)):
            op = "rm"
            page='home.html'
            counter = {
                'count': '0'
            }     
            rpc_obj.manage_pin(phone=phone_num, db_op=op, real_user=True)
            ret = user_cookie(dict=counter, page=page, age=0)
            return ret
        else:
            page = 'auth.html' 
            value = int(request.cookies.get('count'))+1
            counter = {
                'count': str(value)
            }     
            ret = user_cookie(dict=counter, page=page)
            return ret
    return render_template('auth.html')

@app.route('/loginuser', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        rpc_obj = RegistrationClient()
        response = rpc_obj.log_user(request.form.get('uphone'))
        db_pass = response.password
        logging.info('DB_PASS %s', db_pass)
        logging.info('RESP_PASS %s', request.form.get('upass'))
        if(db_pass == request.form.get('upass')):
            logging.info('RESP_PASS_T %s', type(request.form.get('upass')))
            logging.info('DB_PASS_T %s', type(db_pass))

            return(render_template('home.html'))
        else:
            flash('Invalid credentials')
    return render_template('loginuser.html')


def user_cookie(dict, page, age=None):
    resp = make_response(render_template(page))
    for i in dict:
        resp.set_cookie(i, dict[i], max_age=age)
    return resp 



def sms_sender(phone_num):
    #sns = boto3.resource("sns")
    op = 'add'
    pin = randint(100000, 999999)
    message = "This is your account verification pin:{}".format(pin) 
    #sns.meta.client.publish(PhoneNumber=phone_num, Message=message)
    rpc_obj = RegistrationClient()
    try:
        #sns.meta.client.publish(PhoneNumber=phone_num, Message=message)
        logging.info("Published message to %s.", phone_num)
        rpc_obj.manage_pin(phone=phone_num, pin=pin, db_op=op, real_user=False)

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

@app.route('/dashboard', methods=['GET'])
def dashboard():
    username = request.args.get('username', type=str)
    dao = PrescribedDrugsDao(GRPC_PANALYZER_ADDR, GR)
    prescribedDrugs = dao.getPrescribedDrugs(username)
    return render_template('dashboard.html', prescribedDrugs=prescribedDrugs, username=username)
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kafka_port",
        default="9092",
        help="Port of the Kafka server.",
        type=int,
        )
    parser.add_argument(
        "--kafka_addr",
        default="kafka",
        help="Address of the Kafka server.",
        )
    parser.add_argument(
        "--grpc_panalyzer_addr",
        default="prescription-analyzer",
        help="Address of the prescription analyzer gRPC server.",
        )
    parser.add_argument(
        "--grpc_panalyzer_port",
        default="50051",
        help="port of the prescription analyzer gRPC server",
        type=int,
        )
    parser.add_argument(
        "--grpc_manageuser_addr",
        default="manage-user",
        help="Address of the manage user gRPC server.",
        )
    parser.add_argument(
        "--grpc_manageuser_port",
        default="50051",
        help="port of the manage user gRPC server",
        type=int,
        )
    parser.add_argument(
        "--host_addr",
        default="0.0.0.0",
        help="Address of this webserver.",
        )
    parser.add_argument(
        "--host_port",
        default="5000",
        help="Port of this webserver.",
        type=int,
        )
    args = parser.parse_args()

    HOST_ADDR = args.host_addr
    HOST_PORT = args.host_port
    GRPC_MANAGEUSER_ADDR = args.grpc_manageuser_addr
    GRPC_MANAGEUSER_PORT = args.grpc_manageuser_port
    GRPC_PANALYZER_ADDR = args.grpc_panalyzer_addr
    GRPC_PANALYZER_PORT = args.grpc_panalyzer_port

    pub.setKafkaAddr(addr=args.kafka_addr, port=args.kafka_port)

    app.run(debug=True, host=HOST_ADDR)
